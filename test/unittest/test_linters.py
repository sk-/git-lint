# -*- coding: utf-8 -*-
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
from __future__ import unicode_literals

import functools
import os
import subprocess
import unittest

import mock

import gitlint
import gitlint.utils
import gitlint.linters as linters

# pylint: disable=too-many-public-methods,protected-access


class LintersTest(unittest.TestCase):
    def test_lint_command_success(self):
        with mock.patch('subprocess.check_output') as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            check_output.return_value = os.linesep.join([
                'Line 1:1: 1',
                'Line 5:2: 5 ·',
                'Line 7:3: 7',
                'Line 9:4: 9']).encode('utf-8')
            command = functools.partial(
                linters.lint_command,
                'l',
                'linter',
                ['-f', '--compact'],
                r'^Line (?P<line>{lines}):(?P<column>\d+): (?P<message>.*)$')
            filename = 'foo.txt'
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'line': 5,
                                'column': 2,
                                'message': '5 ·'
                            },
                            {
                                'line': 7,
                                'column': 3,
                                'message': '7'
                            },
                        ],
                    },
                },
                command(filename, lines=[3, 5, 7]))
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'line': 1,
                                'column': 1,
                                'message': '1'
                            },
                            {
                                'line': 5,
                                'column': 2,
                                'message': '5 ·'
                            },
                            {
                                'line': 7,
                                'column': 3,
                                'message': '7'
                            },
                            {
                                'line': 9,
                                'column': 4,
                                'message': '9'
                            },
                        ],
                    },
                },
                command(filename, lines=None))
            expected_calls = [
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_command_all_fields(self):
        with mock.patch('subprocess.check_output') as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            check_output.return_value = os.linesep.join(
                ['ERROR: line 1, col 1: (W32) missing foo']).encode('utf-8')
            command = functools.partial(
                linters.lint_command,
                'l',
                'linter',
                ['-f', '--compact'],
                r'^(?P<severity>.*): line (?P<line>{lines})(, col ' +
                r'(?P<column>\d+)): \((?P<message_id>.*)\) (?P<message>.*)$')
            filename = 'foo.txt'
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'line': 1,
                                'column': 1,
                                'message': 'missing foo',
                                'message_id': 'W32',
                                'severity': 'Error',
                            },
                        ],
                    },
                },
                command(filename, lines=None))

    def test_lint_command_error(self):
        output = os.linesep.join([
            'Line 1: 1',
            'Line 5: 5',
            'Line 7: 7',
            'Line 9: 9']).encode('utf-8')
        with mock.patch('subprocess.check_output',
                        side_effect=subprocess.CalledProcessError(
                            1, 'linter', output)) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            command = functools.partial(
                linters.lint_command,
                'l',
                'linter',
                ['-f', '--compact'],
                '^Line (?P<line>{lines}): (?P<message>.*)$')
            filename = 'foo.txt'
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'line': 5,
                                'message': '5'
                            },
                            {
                                'line': 7,
                                'message': '7'
                            },
                        ],
                    },
                },
                command(filename, lines=[3, 5, 7]))
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'line': 1,
                                'message': '1'
                            },
                            {
                                'line': 5,
                                'message': '5'
                            },
                            {
                                'line': 7,
                                'message': '7'
                            },
                            {
                                'line': 9,
                                'message': '9'
                            },
                        ],
                    },
                },
                command(filename, lines=None))
            expected_calls = [
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_command_not_found(self):
        with mock.patch('subprocess.check_output',
                        side_effect=OSError('Not found')) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0]):
            command = functools.partial(linters.lint_command,
                                        'l',
                                        'linter',
                                        ['-f', '--compact'],
                                        '^Line ({lines}):')
            filename = 'foo.txt'
            output = command(filename, lines=[3, 5, 7])
            self.assertEqual(1, len(output[filename]['error']))
            output[filename]['error'] = []
            self.assertTrue(
                {
                    filename: {
                        'error': ''
                    }
                },
                output)
            expected_calls = [
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint(self):
        linter1 = functools.partial(
            linters.lint_command,
            'l1',
            'linter1', ['-f'],
            '^Line (?P<line>{lines}): (?P<message>.*)$')
        linter2 = functools.partial(
            linters.lint_command,
            'l2',
            'linter2', [],
            '^ line (?P<line>{lines}): (?P<message>.*)$')
        config = {
            '.txt': [linter1, linter2]
        }
        outputs = [os.linesep.join(['Line 1: 1', 'Line 5: 5']).encode('utf-8'),
                   os.linesep.join([' line 4: 4']).encode('utf-8')]
        with mock.patch('subprocess.check_output',
                        side_effect=outputs) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            filename = 'foo.txt'
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'line': 4,
                                'message': '4'
                            },
                            {
                                'line': 5,
                                'message': '5'
                            },
                        ],
                    },
                },
                linters.lint(filename, lines=[4, 5], config=config))
            expected_calls = [
                mock.call(['linter1', '-f', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter2', 'foo.txt'], stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_output_is_sorted(self):
        linter1 = functools.partial(
            linters.lint_command,
            'l1',
            'linter1', ['-f'],
            '^Line (?P<line>{lines}): (?P<message>.*)$')
        linter2 = functools.partial(
            linters.lint_command,
            'l2',
            'linter2', [],
            '^ line (?P<line>{lines}): (?P<message>.*)$')
        linter3 = functools.partial(
            linters.lint_command,
            'l3',
            'linter3', [],
            '^(?P<message>.*)$')
        linter4 = functools.partial(
            linters.lint_command,
            'l4',
            'linter4', [],
            r'^(?P<line>{lines}):(?P<column>\d+): (?P<message>.*)$')
        config = {
            '.txt': [linter1, linter2, linter3, linter4]
        }
        outputs = [
            os.linesep.join(['Line 5: 5', 'Line 1: 1']).encode('utf-8'),
            os.linesep.join([' line 4: 4']).encode('utf-8'),
            os.linesep.join(['message']).encode('utf-8'),
            os.linesep.join(['4:10: 4.a', '4:1: 4.b']).encode('utf-8'),
        ]
        with mock.patch('subprocess.check_output', side_effect=outputs), \
                mock.patch('os.path.getmtime', side_effect=[1, 0] * 4):
            filename = 'foo.txt'
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'message': 'message',
                            },
                            {
                                'line': 1,
                                'message': '1',
                            },
                            {
                                'line': 4,
                                'message': '4',
                            },
                            {
                                'line': 4,
                                'column': 1,
                                'message': '4.b',
                            },
                            {
                                'line': 4,
                                'column': 10,
                                'message': '4.a',
                            },
                            {
                                'line': 5,
                                'message': '5',
                            },
                        ],
                    },
                },
                linters.lint(filename, lines=None, config=config))

    def test_lint_one_empty_lint(self):
        linter1 = functools.partial(
            linters.lint_command,
            'l1',
            'linter1',
            ['-f'],
            '^Line (?P<line>{lines}): (?P<message>.*)$')
        linter2 = functools.partial(
            linters.lint_command,
            'l2',
            'linter2',
            [],
            '^ line (?P<line>{lines}): (?P<message>.*)$')
        config = {
            '.txt': [linter1, linter2]
        }
        outputs = [b'',
                   os.linesep.join([' line 4: 4']).encode('utf-8')]
        with mock.patch('subprocess.check_output',
                        side_effect=outputs) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            filename = 'foo.txt'
            self.assertEqual(
                {
                    filename: {
                        'comments': [
                            {
                                'line': 4,
                                'message': '4'
                            },
                        ],
                    },
                },
                linters.lint(filename, lines=[4, 5], config=config))
            expected_calls = [
                mock.call(['linter1', '-f', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter2', 'foo.txt'], stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_all_empty_lint(self):
        linter1 = functools.partial(
            linters.lint_command, 'l1', 'linter1', ['-f'], '^Line {lines}:')
        linter2 = functools.partial(
            linters.lint_command, 'l2', 'linter2', [], '^ line {lines}:')
        config = {
            '.txt': [linter1, linter2]
        }
        outputs = [b'', b'']
        with mock.patch('subprocess.check_output',
                        side_effect=outputs) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            filename = 'foo.txt'
            self.assertEqual(
                {
                    filename: {
                        'comments': []
                    }
                },
                linters.lint(filename, lines=[4, 5], config=config))
            expected_calls = [
                mock.call(['linter1', '-f', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter2', 'foo.txt'], stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_extension_not_defined(self):
        config = {}
        output = linters.lint('foo.txt', lines=[4, 5], config=config)
        self.assertEqual(1, len(output['foo.txt']['skipped']))
        output['foo.txt']['skipped'] = []
        self.assertEqual(
            {
                'foo.txt': {
                    'skipped': []
                }
            },
            output)

    def test_lint_missing_programs(self):
        linter1 = functools.partial(
            linters.missing_requirements_command,
            'l1', ['p1', 'p2'], 'Install p1 and p2')
        config = {
            '.txt': [linter1]
        }
        output = linters.lint('foo.txt', lines=[4, 5], config=config)
        self.assertEqual(1, len(output['foo.txt']['skipped']))
        output['foo.txt']['skipped'] = []
        self.assertEqual(
            {
                'foo.txt': {
                    'skipped': []
                }
            },
            output)

    def test_lint_two_missing_programs(self):
        linter1 = functools.partial(
            linters.missing_requirements_command,
            'l1', ['p1', 'p2'], 'Install p1 and p2')
        config = {
            '.txt': [linter1, linter1]
        }
        output = linters.lint('foo.txt', lines=[4, 5], config=config)
        self.assertEqual(2, len(output['foo.txt']['skipped']))
        output['foo.txt']['skipped'] = []
        self.assertEqual(
            {
                'foo.txt': {
                    'skipped': []
                }
            },
            output)

    def test_parse_yaml_config_command_not_in_path(self):
        yaml_config = {
            'linter': {
                'arguments': [],
                'command': 'some_unexistent_program_name',
                'extensions': ['.foo'],
                'filter': '.*',
                'installation': ('Go to some_unexistent_program_name.com to ' +
                                 'install it.'),
            }
        }
        config = linters.parse_yaml_config(yaml_config, '')
        self.assertEqual(
            {
                'filename': {
                    'skipped': ['some_unexistent_program_name is not ' +
                                'installed. Go to some_unexistent_program_' +
                                'name.com to install it.']
                }
            },
            config['.foo'][0]('filename', []))

    def test_parse_yaml_config_requirements_not_in_path(self):
        yaml_config = {
            'linter': {
                'arguments': [],
                'command': 'ls',
                'requirements': [
                    'some_unexistent_command_one',
                    'ls',
                    'some_unexistent_command_two',
                ],
                'extensions': ['.foo'],
                'filter': '.*',
                'installation': 'Run apt-get install command_one command_two',
            }
        }
        config = linters.parse_yaml_config(yaml_config, '')
        self.assertEqual(
            {
                'filename': {
                    'skipped': ['some_unexistent_command_one, ' +
                                'some_unexistent_command_two are not '
                                'installed. Run apt-get install command_one ' +
                                'command_two']
                }
            },
            config['.foo'][0]('filename', []))

    def test_parse_yaml_config_with_variables(self):
        yaml_config_with_vars = {
            'linter': {
                'arguments': [
                    '--config',
                    '{DEFAULT_CONFIGS}/foo.config'
                ],
                'command': '{REPO_HOME}/bin/linter',
                'requirements': [
                    '{REPO_HOME}/bin/dep1',
                ],
                'extensions': ['.foo'],
                'filter': '.*',
                'installation': 'install',
            }
        }
        variables = {
            'DEFAULT_CONFIGS': os.path.join(os.path.dirname(gitlint.__file__),
                                            'configs'),
            'REPO_HOME': '/usr/home/repo',
        }
        yaml_config_no_vars = {
            'linter': {
                'arguments': [
                    '--config',
                    '{DEFAULT_CONFIGS}/foo.config'.format(**variables),
                ],
                'command': '{REPO_HOME}/bin/linter'.format(**variables),
                'requirements': [
                    '{REPO_HOME}/bin/dep1'.format(**variables),
                ],
                'extensions': ['.foo'],
                'filter': '.*',
                'installation': 'install',
            }
        }

        with mock.patch('gitlint.utils.which', return_value=['lint']):
            config_with_vars = linters.parse_yaml_config(
                yaml_config_with_vars, variables['REPO_HOME'])
            config_no_vars = linters.parse_yaml_config(
                yaml_config_no_vars, variables['REPO_HOME'])

            self.assertEqual(config_with_vars, config_no_vars)
