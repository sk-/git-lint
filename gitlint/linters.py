# Copyright 2013 Sebastian Kreft
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
import collections
import functools
import os.path
import subprocess

import yaml

import gitlint.utils as utils


def filter_output(output, pattern):
    """Filters out the lines not matching the pattern.

    A line is defined to be anything surrounded by the start of file, end of
    file or os.linesep.

    Args:
      output: string: string containing the lines to filter.
      pattern: string: regular expression to filter out lines.

    Returns: string: the list of filtered lines.
    """
    return os.linesep.join(utils.filter_lines(output.split(os.linesep), pattern))


def lint_command(program, arguments, filter_regex, filename, lines):
    """Executes a lint program and filter the output.

    Executes the lint tool 'program' with arguments 'arguments' over the file
    'filename' returning only those lines matching the regular expression
    'filter_regex'.

    Args:
      program: string: lint program.
      arguments: list[string]: extra arguments for the program.
      filter_regex: string: regular expression to filter lines.
      filename: string: filename to lint.
      lines: list[int]|None: list of lines that we want to capture. If None,
        then all lines will be captured.

    Returns: string: a string with the filtered output of the program.
    """
    call_arguments = [program] + arguments + [filename]
    try:
        output = subprocess.check_output(call_arguments,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        output = error.output
    except OSError:
        return ('ERROR: could not execute "%s".\nMake sure all required ' +
                'programs are installed') % ' '.join(call_arguments)

    if lines is None:
        lines_regex = r'\d+'
    else:
        lines_regex = '|'.join(map(str, lines))
    filtered_output = filter_output(output,
                                    filter_regex % {'lines': lines_regex,
                                                    'filename': filename})

    return filtered_output


def get_config():
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
        yaml_config = yaml.load(f)
    config = collections.defaultdict(list)

    for data in yaml_config.itervalues():
        for extension in data['extensions']:
            if extension not in ['.js', '.py', '.css', '.php']: #, '.jpg']:
                continue
            config[extension].append(
                functools.partial(lint_command,
                                  data['command'],
                                  data.get('arguments', []),
                                  data['filter']))

    return config

_EXTENSION_TO_LINTER = get_config()


def lint(filename, lines, config):
    """Lints a file.

    Args:
        filename: string: filename to lint.
        lines: list[int]|None: list of lines that we want to capture. If None,
          then all lines will be captured.
        config: dict[string: linter]: mapping from extension to a linter
          function.

    Returns: string: 'OK' when succesful, a string starting with 'SKIPPED' in
    case there was no linter defined for the file, or the output of the linter
    with the lines filtered.
    """
    _, ext = os.path.splitext(filename)
    if ext in config:
        linters_output = []
        for linter in config[ext]:
            linter_output = linter(filename, lines)
            if linter_output:
                linters_output.append(linter_output)
        output = os.linesep.join(linters_output)
        if not output:
            return 'OK'
        return output
    else:
        return ('SKIPPED: no linter is defined or enabled for files with '
                'extension "%s"' % ext)
