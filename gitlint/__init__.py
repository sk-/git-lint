# Copyright 2013-2014 Sebastian Kreft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
git-lint: improving source code one step at a time

Lints all the modified files in your git repository showing only the modified
lines.

It supports many filetypes, including:
    PHP, Python, Javascript, Ruby, CSS, SCSS, PNG, JPEG, RST, YAML, INI, Java,
    among others. See https://github.com/sk-/git-lint for the complete list.

Usage:
    git-lint [-f | --force] [--json] [--last-commit] [FILENAME ...]
    git-lint [-t | --tracked] [-f | --force] [--json] [--last-commit]
    git-lint -h | --version

Options:
    -h             Show the usage patterns.
    --version      Prints the version number.
    -f --force     Shows all the lines with problems.
    -t --tracked   Lints only tracked files.
    --json         Prints the result as a json string. Useful to use it in
                   conjunction with other tools.
    --last-commit  Checks the last checked-out commit. This is mostly useful
                   when used as: git checkout <revid>; git lint --last-commit.
"""

from __future__ import unicode_literals

import codecs
import json
import os
import os.path
import sys

import docopt
import termcolor
import yaml

import gitlint.git as git
import gitlint.linters as linters


__VERSION__ = '0.0.2'


def find_invalid_filenames(filenames, repository_root):
    """Find files that does not exist, are not in the repo or are directories.

    Args:
      filenames: list of filenames to check
      repository_root: the absolute path of the repository's root.

    Returns: A list of errors.
    """
    errors = []
    for filename in filenames:
        if not os.path.abspath(filename).startswith(repository_root):
            errors.append((filename, 'Error: File %s does not belong to '
                          'repository %s' % (filename, repository_root)))
        if not os.path.exists(filename):
            errors.append((filename,
                          'Error: File %s does not exist' % (filename, )))
        if os.path.isdir(filename):
            errors.append((filename, 'Error: %s is a directory. Directories are'
                          ' not yet supported' % (filename, )))

    return errors


def get_config():
    """Gets the configuration file either from the repository or the default."""
    config = os.path.join(os.path.dirname(__file__), 'configs', 'config.yaml')
    repo_root = git.repository_root()

    if repo_root:
        repo_config = os.path.join(repo_root, '.gitlint.yaml')
        if os.path.exists(repo_config):
            config = repo_config

    with open(config) as f:
        # We have to read the content first as yaml hangs up when reading from
        # MockOpen
        content = f.read()
        # Yaml.load will return None when the input is empty.
        if not content:
            yaml_config = {}
        else:
            yaml_config = yaml.load(content)

    return linters.parse_yaml_config(yaml_config, repo_root)


def format_comment(comment_data):
    """Formats the data returned by the linters.

    Given a dictionary with the fields: line, column, severity, message_id,
    message, will generate a message like:

    'line {line}, col {column}: {severity}: [{message_id}]: {message}'

    Any of the fields may nbe absent.

    Args:
      comment_data: dictionary with the linter data.

    Returns:
      a string with the formatted message.
    """
    format_pieces = []
    # Line and column information
    if 'line' in comment_data:
        format_pieces.append('line {line}')
    if 'column' in comment_data:
        if format_pieces:
            format_pieces.append(', ')
        format_pieces.append('col {column}')
    if format_pieces:
        format_pieces.append(': ')

    # Severity and Id information
    if 'severity' in comment_data:
        format_pieces.append('{severity}: ')

    if 'message_id' in comment_data:
        format_pieces.append('[{message_id}]: ')

    # The message
    if 'message' in comment_data:
        format_pieces.append('{message}')

    return ''.join(format_pieces).format(**comment_data)


def main(argv, stdout=sys.stdout, stderr=sys.stderr):
    """Main gitlint routine. To be called from scripts."""
    # Wrap sys stdout for python 2, so print can understand unicode.
    linesep = os.linesep
    if sys.version_info[0] < 3:
        if stdout == sys.stdout:
            stdout = codecs.getwriter("utf-8")(stdout)
        if stderr == sys.stderr:
            stderr = codecs.getwriter("utf-8")(stderr)
        linesep = unicode(os.linesep)

    arguments = docopt.docopt(__doc__,
                              argv=argv[1:],
                              version='git-lint v%s' % __VERSION__)

    json_output = arguments['--json']

    commit = None
    if arguments['--last-commit']:
        commit = git.last_commit()

    repository_root = git.repository_root()
    if repository_root is None:
        stderr.write('fatal: Not a git repository' + os.linesep)
        return 128

    if arguments['FILENAME']:
        invalid_filenames = find_invalid_filenames(arguments['FILENAME'],
                                                   repository_root)
        if invalid_filenames:
            invalid_filenames.append(('', ''))
            stderr.write(
                os.linesep.join(invalid[1] for invalid in invalid_filenames))
            return 2

        changed_files = git.modified_files(repository_root,
                                           tracked_only=arguments['--tracked'],
                                           commit=commit)
        modified_files = {}
        for filename in arguments['FILENAME']:
            normalized_filename = os.path.abspath(filename)
            modified_files[normalized_filename] = changed_files.get(
                normalized_filename)
    else:
        modified_files = git.modified_files(repository_root,
                                            tracked_only=arguments['--tracked'],
                                            commit=commit)

    linter_not_found = False
    files_with_problems = 0
    gitlint_config = get_config()
    json_result = {}

    error = termcolor.colored('ERROR', 'red', attrs=('bold',))
    skipped = termcolor.colored('SKIPPED', 'yellow', attrs=('bold',))

    for filename in sorted(modified_files.keys()):
        rel_filename = os.path.relpath(filename)
        if not json_output:
            stdout.write('Linting file: %s%s' %
                         (termcolor.colored(rel_filename, attrs=('bold',)),
                          linesep))
        if arguments['--force']:
            modified_lines = None
        else:
            modified_lines = git.modified_lines(filename,
                                                modified_files[filename],
                                                commit=commit)

        result = linters.lint(
            filename, modified_lines, gitlint_config)
        result = result[filename]

        output = ''
        if result.get('error'):
            output += os.linesep.join(
                '%s: %s' % (error, reason) for reason in result.get('error')
            )
            linter_not_found = True
        if result.get('skipped'):
            output += os.linesep.join(
                '%s: %s' % (skipped, reason) for reason in result.get('skipped')
            )
        if result.get('comments', []) == []:
            if not output:
                output += termcolor.colored('OK', 'green', attrs=('bold',))
        else:
            files_with_problems += 1
            output += os.linesep.join(format_comment(data)
                                      for data in result['comments'])

        if json_output:
            json_result[filename] = result
        else:
            stdout.write(output)
            stdout.write(linesep + linesep)

    if json_output:
        # Hack to convert to unicode, Python3 returns unicode, wheres Python2
        # returns str.
        stdout.write(
            json.dumps(json_result,
                       ensure_ascii=False).encode('utf-8').decode('utf-8'))

    if files_with_problems > 0:
        return 1
    if linter_not_found:
        return 4
    return 0
