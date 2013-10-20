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
"""Functions for invoking a lint command."""

import collections
import functools
import os.path
import subprocess

import yaml

import gitlint.utils as utils


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

    output_lines = output.split(os.linesep)

    if lines is None:
        lines_regex = r'\d+'
    else:
        lines_regex = '|'.join(map(str, lines))

    filtered_lines = utils.filter_lines(output_lines,
                                        filter_regex % {'lines': lines_regex,
                                                        'filename': filename})

    return os.linesep.join(filtered_lines)


def get_config():
    """Returns a dictionary that maps from an extension to a list of linters."""
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml')) as f:
        yaml_config = yaml.load(f)
    config = collections.defaultdict(list)

    for data in yaml_config.itervalues():
        for extension in data['extensions']:
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
