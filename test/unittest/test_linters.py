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
import functools
import os
import subprocess
import unittest

import mock

import gitlint.linters as linters

# pylint: disable=too-many-public-methods,protected-access


class LintersTest(unittest.TestCase):
    def test_lint_command_success(self):
        with mock.patch('subprocess.check_output') as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            check_output.return_value = os.linesep.join(
                ['Line 1: 1', 'Line 5: 5', 'Line 7: 7', 'Line 9: 9'])
            command = functools.partial(linters.lint_command,
                                        'l',
                                        'linter',
                                        ['-f', '--compact'],
                                        '^Line (%(lines)s):')
            filename = 'foo.txt'
            self.assertEqual(os.linesep.join(['Line 5: 5', 'Line 7: 7']),
                             command(filename, lines=[3, 5, 7]))
            self.assertEqual(
                os.linesep.join(
                    ['Line 1: 1', 'Line 5: 5', 'Line 7: 7', 'Line 9: 9']),
                command(filename, lines=None))
            expected_calls = [
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_command_error(self):
        output = os.linesep.join(
            ['Line 1: 1', 'Line 5: 5', 'Line 7: 7', 'Line 9: 9'])
        with mock.patch('subprocess.check_output',
                        side_effect=subprocess.CalledProcessError(
                            1, 'linter', output)) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            command = functools.partial(linters.lint_command,
                                        'l',
                                        'linter',
                                        ['-f', '--compact'],
                                        '^Line (%(lines)s):')
            filename = 'foo.txt'
            self.assertEqual(os.linesep.join(['Line 5: 5', ('Line 7: 7')]),
                             command(filename, lines=[3, 5, 7]))
            self.assertEqual(
                os.linesep.join(
                    ['Line 1: 1', 'Line 5: 5', 'Line 7: 7', 'Line 9: 9']),
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
                                        '^Line (%(lines)s):')
            filename = 'foo.txt'
            self.assertTrue(
                command(filename, lines=[3, 5, 7]).startswith('ERROR:'))
            expected_calls = [
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_command_pattern_no_parentheses(self):
        with mock.patch('subprocess.check_output') as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            check_output.return_value = os.linesep.join(
                ['Line 1: col 14: undefined', 'Line 5: 5', 'Line 7: 7'])
            command = functools.partial(linters.lint_command,
                                        'l',
                                        'linter',
                                        ['-f', '--compact'],
                                        '^Line %(lines)s:')
            filename = 'foo.txt'
            self.assertEqual(os.linesep.join(['Line 7: 7']),
                             command(filename, lines=[3, 7, 14]))
            self.assertEqual(
                os.linesep.join(
                    ['Line 1: col 14: undefined', 'Line 5: 5', 'Line 7: 7']),
                command(filename, lines=None))
            expected_calls = [
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter', '-f', '--compact', 'foo.txt'],
                          stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint(self):
        linter1 = functools.partial(linters.lint_command,
                                    'l1',
                                    'linter1', ['-f'],
                                    '^Line (%(lines)s):')
        linter2 = functools.partial(linters.lint_command,
                                    'l2',
                                    'linter2', [],
                                    '^ line (%(lines)s):')
        config = {
            '.txt': [linter1, linter2]
        }
        outputs = [os.linesep.join(['Line 1: 1', 'Line 5: 5']),
                   os.linesep.join([' line 4: 4'])]
        with mock.patch('subprocess.check_output',
                        side_effect=outputs) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            filename = 'foo.txt'
            self.assertEqual(
                os.linesep.join(['Line 5: 5', ' line 4: 4']),
                linters.lint(filename, lines=[4, 5], config=config))
            expected_calls = [
                mock.call(['linter1', '-f', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter2', 'foo.txt'], stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_one_empty_lint(self):
        linter1 = functools.partial(
            linters.lint_command, 'l1', 'linter1', ['-f'], '^Line (%(lines)s):')
        linter2 = functools.partial(
            linters.lint_command, 'l2', 'linter2', [], '^ line (%(lines)s):')
        config = {
            '.txt': [linter1, linter2]
        }
        outputs = ['',
                   os.linesep.join([' line 4: 4'])]
        with mock.patch('subprocess.check_output',
                        side_effect=outputs) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            filename = 'foo.txt'
            self.assertEqual(
                ' line 4: 4',
                linters.lint(filename, lines=[4, 5], config=config))
            expected_calls = [
                mock.call(['linter1', '-f', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter2', 'foo.txt'], stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_all_empty_lint(self):
        linter1 = functools.partial(
            linters.lint_command, 'l1', 'linter1', ['-f'], '^Line %(lines)s:')
        linter2 = functools.partial(
            linters.lint_command, 'l2', 'linter2', [], '^ line %(lines)s:')
        config = {
            '.txt': [linter1, linter2]
        }
        outputs = ['', '']
        with mock.patch('subprocess.check_output',
                        side_effect=outputs) as check_output, \
                mock.patch('os.path.getmtime', side_effect=[1, 0, 1, 0]):
            filename = 'foo.txt'
            self.assertEqual(
                'OK', linters.lint(filename, lines=[4, 5], config=config))
            expected_calls = [
                mock.call(['linter1', '-f', 'foo.txt'],
                          stderr=subprocess.STDOUT),
                mock.call(['linter2', 'foo.txt'], stderr=subprocess.STDOUT)]
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_lint_extension_not_defined(self):
        config = {}
        output = linters.lint('foo.txt', lines=[4, 5], config=config)
        self.assertIn('.txt', output)
        self.assertTrue(output.startswith('SKIPPED'))

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
        config = linters._parse_yaml_config(yaml_config)
        self.assertEqual(
            'SKIPPED: some_unexistent_program_name is not installed. Go to ' +
            'some_unexistent_program_name.com to install it.',
            config['.foo'][0]('filename', []))
