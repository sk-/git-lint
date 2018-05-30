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

import io
import json
import os
import sys

import mock
from pyfakefs import fake_filesystem_unittest

import gitlint

# pylint: disable=too-many-public-methods


class GitLintTest(fake_filesystem_unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._stderr = sys.stderr
        sys.stderr = sys.stdout

    @classmethod
    def tearDownClass(cls):
        sys.stderr = cls._stderr

    def setUp(self):
        self.original_config_file = os.path.join(
            os.path.dirname(gitlint.__file__), 'configs', 'config.yaml')
        self.setUpPyfakefs()
        self.fs.add_real_file(self.original_config_file)

        self.root = '/home/user/repo'
        self.fs.create_dir(self.root)
        os.chdir(self.root)
        self.filename = os.path.join(self.root, 'changed.py')
        self.filename2 = os.path.join(self.root, 'foo.txt')

        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

        self.git_repository_root_patch = mock.patch(
            'gitlint.git.repository_root', return_value=self.root)
        self.git_repository_root = self.git_repository_root_patch.start()
        self.addCleanup(self.git_repository_root_patch.stop)

        self.hg_repository_root_patch = mock.patch(
            'gitlint.hg.repository_root', return_value=None)
        self.hg_repository_root = self.hg_repository_root_patch.start()
        self.addCleanup(self.hg_repository_root_patch.stop)

        self.git_modified_files_patch = mock.patch(
            'gitlint.git.modified_files', return_value={self.filename: ' M'})
        self.git_modified_files = self.git_modified_files_patch.start()
        self.addCleanup(self.git_modified_files_patch.stop)

        self.git_modified_lines_patch = mock.patch(
            'gitlint.git.modified_lines', return_value=[3, 14])
        self.git_modified_lines = self.git_modified_lines_patch.start()
        self.addCleanup(self.git_modified_lines_patch.stop)

        self.git_last_commit_patch = mock.patch(
            'gitlint.git.last_commit', return_value="abcd" * 10)
        self.git_last_commit = self.git_last_commit_patch.start()
        self.addCleanup(self.git_last_commit_patch.stop)

        self.lint_patch = mock.patch('gitlint.linters.lint')
        self.lint = self.lint_patch.start()
        self.addCleanup(self.lint_patch.stop)

    def reset_mock_calls(self):
        """Resets the counter calls of the defined mocks."""
        self.git_repository_root.reset_mock()
        self.git_modified_files.reset_mock()
        self.git_modified_lines.reset_mock()
        self.lint.reset_mock()

    def assert_mocked_calls(self, tracked_only=False, commit=None):
        """Checks if the mocks were called as expected.

        This method exists to avoid duplication.
        """
        self.git_modified_files.assert_called_once_with(
            self.root, tracked_only=tracked_only, commit=commit)
        self.git_modified_lines.assert_called_once_with(
            self.filename, ' M', commit=commit)
        self.lint.assert_called_once_with(self.filename, [3, 14], mock.ANY)

    def test_find_invalid_filenames(self):
        file_outside_repo = '/tmp/outside_repo'
        inexistent_file = os.path.join(self.root, 'inexistent_file')
        directory_in_repo = os.path.join(self.root, 'directory_in_repo')
        valid_file = os.path.join(self.root, 'valid')
        filenames = [
            file_outside_repo, inexistent_file, directory_in_repo, valid_file
        ]
        expected = {
            file_outside_repo: 'does not belong to repository',
            inexistent_file: 'does not exist',
            directory_in_repo: 'Directories are not yet supported',
        }

        self.fs.create_file(file_outside_repo)
        self.fs.create_dir(directory_in_repo)
        self.fs.create_file(valid_file)

        invalid_filenames = dict(
            gitlint.find_invalid_filenames(filenames, self.root))

        self.assertEqual(expected.keys(), invalid_filenames.keys())
        for filename in invalid_filenames:
            self.assertIn(filename, invalid_filenames[filename])
            self.assertIn(expected[filename], invalid_filenames[filename])

    def test_main_not_in_repo(self):
        self.git_repository_root.return_value = None
        self.assertEqual(128, gitlint.main(
            [], stdout=None, stderr=self.stderr))
        self.assertIn('Not a git repository', self.stderr.getvalue())

    def test_main_nothing_changed(self):
        self.git_modified_files.return_value = {}
        self.assertEqual(0, gitlint.main([], stdout=None, stderr=None))
        self.git_modified_files.assert_called_once_with(
            self.root, tracked_only=False, commit=None)

    def test_main_file_changed_and_still_valid(self):
        lint_response = {self.filename: {'comments': []}}
        self.lint.return_value = lint_response

        self.assertEqual(0, gitlint.main([], stdout=self.stdout, stderr=None))
        self.assertIn('OK', self.stdout.getvalue())
        self.assert_mocked_calls()

    def test_main_file_changed_and_still_valid_with_commit(self):
        lint_response = {self.filename: {'comments': []}}
        self.lint.return_value = lint_response

        self.assertEqual(
            0,
            gitlint.main(
                ['git-lint', '--last-commit'], stdout=self.stdout,
                stderr=None))
        self.assertIn('OK', self.stdout.getvalue())
        self.assert_mocked_calls(commit='abcd' * 10)

    def test_main_file_changed_and_still_valid_tracked_only(self):
        lint_response = {self.filename: {'comments': []}}
        self.lint.return_value = lint_response

        self.assertEqual(
            0, gitlint.main(
                ['git-lint', '-t'], stdout=self.stdout, stderr=None))
        self.assertIn('OK', self.stdout.getvalue())
        self.assert_mocked_calls(tracked_only=True)

        self.reset_mock_calls()
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

        self.assertEqual(
            0,
            gitlint.main(
                ['git-lint', '--tracked'], stdout=self.stdout, stderr=None))
        self.assertIn('OK', self.stdout.getvalue())
        self.assert_mocked_calls(tracked_only=True)

    def test_main_file_changed_but_skipped(self):
        lint_response = {self.filename: {'skipped': ['foo']}}
        self.lint.return_value = lint_response

        self.assertEqual(0, gitlint.main([], stdout=self.stdout, stderr=None))
        self.assertIn('SKIPPED', self.stdout.getvalue())
        self.assert_mocked_calls()

    def test_main_file_linter_not_found(self):
        lint_response = {self.filename: {'error': ['foo']}}
        self.lint.return_value = lint_response

        self.assertEqual(4, gitlint.main([], stdout=self.stdout, stderr=None))
        self.assertIn('ERROR', self.stdout.getvalue())
        self.assert_mocked_calls()

    def test_main_file_changed_and_now_invalid(self):
        lint_response = {
            self.filename: {
                'comments': [{
                    'line': 3,
                    'message': 'error'
                }]
            }
        }
        self.lint.return_value = lint_response

        self.assertEqual(1, gitlint.main([], stdout=self.stdout, stderr=None))
        self.assertIn('line 3: error', self.stdout.getvalue())
        self.assert_mocked_calls()

    def test_main_file_with_skipped_error_and_comments(self):
        lint_response = {
            self.filename: {
                'skipped': ['skipped1', 'skipped2'],
                'error': ['error1', 'error2'],
                'comments': [{
                    'line': 3,
                    'message': 'message1'
                }, {
                    'line': 4,
                    'message': 'message2'
                }]
            }
        }
        self.lint.return_value = lint_response

        self.assertEqual(1, gitlint.main([], stdout=self.stdout, stderr=None))
        self.assertIn('line 3: message1', self.stdout.getvalue())
        self.assertIn('line 4: message2', self.stdout.getvalue())
        self.assertIn('skipped1', self.stdout.getvalue())
        self.assertIn('skipped2', self.stdout.getvalue())
        self.assertIn('error1', self.stdout.getvalue())
        self.assertIn('error2', self.stdout.getvalue())
        self.assert_mocked_calls()

    def test_main_file_json(self):
        self.git_modified_files.return_value = {
            self.filename: ' M',
            self.filename2: 'M ',
        }
        lint_responses = [{
            self.filename: {
                'skipped': ['skipped1', 'skipped2'],
                'error': ['error1', 'error2'],
                'comments': [{
                    'line': 3,
                    'message': 'message1'
                }, {
                    'line': 4,
                    'message': 'message2'
                }]
            }
        }, {
            self.filename2: {
                'comments': []
            },
        }]
        self.lint.side_effect = lint_responses
        expected_response = {
            self.filename: {
                'skipped': ['skipped1', 'skipped2'],
                'error': ['error1', 'error2'],
                'comments': [{
                    'line': 3,
                    'message': 'message1',
                    'formatted_message': 'line 3: message1'
                }, {
                    'line': 4,
                    'message': 'message2',
                    'formatted_message': 'line 4: message2'
                }]
            },
            self.filename2: {
                'comments': []
            },
        }

        self.assertEqual(
            1,
            gitlint.main(
                ['git-lint', '--json'], stdout=self.stdout, stderr=None))
        self.assertEqual(expected_response, json.loads(self.stdout.getvalue()))

    def test_main_file_with_skipped_and_error(self):
        lint_response = {
            self.filename: {
                'skipped': ['skipped1'],
                'error': ['error1'],
                'comments': []
            }
        }
        self.lint.return_value = lint_response

        self.assertEqual(4, gitlint.main([], stdout=self.stdout, stderr=None))
        self.assertNotIn('OK', self.stdout.getvalue())
        self.assertIn('skipped1', self.stdout.getvalue())
        self.assertIn('error1', self.stdout.getvalue())
        self.assert_mocked_calls()

    def test_main_force_all_lines(self):
        lint_response = {
            self.filename: {
                'comments': [{
                    'line': 3,
                    'message': 'error'
                }]
            }
        }
        self.lint.return_value = lint_response
        self.git_modified_lines.return_value = []

        self.assertEqual(
            1,
            gitlint.main(
                ['git-lint', '--force'], stdout=self.stdout, stderr=None))
        self.assertIn('line 3: error', self.stdout.getvalue())

        self.git_modified_files.assert_called_once_with(
            self.root, tracked_only=False, commit=None)
        self.lint.assert_called_once_with(self.filename, None, mock.ANY)

        self.reset_mock_calls()
        self.stdout = io.StringIO()

        self.assertEqual(
            1, gitlint.main(
                ['git-lint', '-f'], stdout=self.stdout, stderr=None))
        self.assertIn('line 3: error', self.stdout.getvalue())

        self.git_modified_files.assert_called_once_with(
            self.root, tracked_only=False, commit=None)
        self.lint.assert_called_once_with(self.filename, None, mock.ANY)

    def test_main_with_invalid_files(self):
        with mock.patch(
                'gitlint.find_invalid_filenames',
                return_value=[('foo.txt', 'does not exist')]):
            self.assertEqual(
                2,
                gitlint.main(
                    ['git-lint', 'foo.txt'], stdout=None, stderr=self.stderr))
            self.assertIn('does not exist', self.stderr.getvalue())

    def test_main_with_valid_files(self):
        lint_response = {
            self.filename: {
                'comments': []
            },
            self.filename2: {
                'comments': []
            },
        }
        self.lint.return_value = lint_response

        with mock.patch('gitlint.find_invalid_filenames', return_value=[]):
            self.assertEqual(
                0,
                gitlint.main(
                    ['git-lint', self.filename, self.filename2],
                    stdout=self.stdout,
                    stderr=None))
            self.assertIn('OK', self.stdout.getvalue())
            self.assertIn(
                os.path.basename(self.filename), self.stdout.getvalue())
            self.assertIn(
                os.path.basename(self.filename2), self.stdout.getvalue())

            self.git_modified_files.assert_called_once_with(
                self.root, tracked_only=False, commit=None)
            expected_calls = [
                mock.call(self.filename, ' M', commit=None),
                mock.call(self.filename2, None, commit=None),
            ]
            self.assertEqual(expected_calls,
                             self.git_modified_lines.call_args_list)
            expected_calls = [
                mock.call(self.filename, [3, 14], mock.ANY),
                mock.call(self.filename2, [3, 14], mock.ANY)
            ]
            self.assertEqual(expected_calls, self.lint.call_args_list)

    def test_main_with_valid_files_relative(self):
        lint_response = {
            self.filename: {
                'comments': []
            },
            self.filename2: {
                'comments': []
            },
        }
        self.lint.return_value = lint_response

        with mock.patch('gitlint.find_invalid_filenames', return_value=[]):
            self.assertEqual(
                0,
                gitlint.main(
                    ['git-lint', 'bar/../changed.py', './foo.txt'],
                    stdout=self.stdout,
                    stderr=self.stderr))
            self.assertIn('OK', self.stdout.getvalue())
            self.assertEqual('', self.stderr.getvalue())

            self.git_modified_files.assert_called_once_with(
                self.root, tracked_only=False, commit=None)
            expected_calls = [
                mock.call(self.filename, ' M', commit=None),
                mock.call(self.filename2, None, commit=None)
            ]
            self.assertEqual(expected_calls,
                             self.git_modified_lines.call_args_list)
            expected_calls = [
                mock.call(self.filename, [3, 14], mock.ANY),
                mock.call(self.filename2, [3, 14], mock.ANY)
            ]
            self.assertEqual(expected_calls, self.lint.call_args_list)

    def test_main_errors_skipped_comments(self):
        lint_response = {
            self.filename: {
                'error': ['error1', 'error2'],
                'skipped': ['skipped1', 'skipped2'],
                'comments': [{
                    'message': 'msg1'
                }, {
                    'message': 'msg2'
                }],
            },
            self.filename2: {
                'comments': [],
            }
        }
        self.lint.return_value = lint_response

        with mock.patch('gitlint.find_invalid_filenames', return_value=[]):
            self.assertEqual(
                1,
                gitlint.main(
                    ['git-lint', self.filename, self.filename2],
                    stdout=self.stdout,
                    stderr=None))
            expected_output = os.linesep.join([
                '\x1b[1m\x1b[31mERROR\x1b[0m: error1',
                '\x1b[1m\x1b[31mERROR\x1b[0m: error2',
                '\x1b[1m\x1b[33mSKIPPED\x1b[0m: skipped1',
                '\x1b[1m\x1b[33mSKIPPED\x1b[0m: skipped2',
                'msg1',
                'msg2',
            ])
            self.assertIn(expected_output, self.stdout.getvalue())

    def test_get_config(self):
        config = """python:
  extensions:
  - .py
  command: python
  arguments:
  - "-R"
  - "-v"
  filter: ".*"
  installation: "Really?"
"""
        self.fs.create_file(
            os.path.join(self.root, '.gitlint.yaml'), contents=config)
        parsed_config = gitlint.get_config(self.root)
        self.assertEqual(['.py'], list(parsed_config.keys()))
        self.assertEqual(1, len(parsed_config['.py']))

    def test_get_config_from_default(self):
        parsed_config = gitlint.get_config(self.root)
        self.assertEqual(gitlint.get_config(None), parsed_config)

    def test_get_config_not_in_a_repo(self):
        # When not in a repo should return the default config.
        self.git_repository_root.return_value = None
        parsed_config = gitlint.get_config(self.root)
        self.assertEqual(gitlint.get_config(None), parsed_config)

    def test_get_config_empty(self):
        self.fs.create_file(os.path.join(self.root, '.gitlint.yaml'))
        # When config file is empty return an empty dictionary.
        parsed_config = gitlint.get_config(self.root)
        self.assertEqual({}, parsed_config)

    def test_format_comment(self):
        self.assertEqual('', gitlint.format_comment({}))
        self.assertEqual(
            'line 1: message',
            gitlint.format_comment({
                'line': 1,
                'message': 'message',
            }))
        self.assertEqual(
            'line 1, col 2: message',
            gitlint.format_comment({
                'line': 1,
                'column': 2,
                'message': 'message',
            }))
        self.assertEqual(
            'line 1, col 2: Error: message',
            gitlint.format_comment({
                'line': 1,
                'column': 2,
                'severity': 'Error',
                'message': 'message',
            }))
        self.assertEqual(
            'line 1, col 2: Error: [not-used]: message',
            gitlint.format_comment({
                'line': 1,
                'column': 2,
                'severity': 'Error',
                'message_id': 'not-used',
                'message': 'message',
            }))
        self.assertEqual(
            'col 2: [not-used]: message',
            gitlint.format_comment({
                'column': 2,
                'message_id': 'not-used',
                'message': 'message',
            }))
        self.assertEqual(
            'line 1, col 2: Error: [not-used]: ',
            gitlint.format_comment({
                'line': 1,
                'column': 2,
                'severity': 'Error',
                'message_id': 'not-used',
            }))

    def test_get_vcs_git(self):
        self.git_repository_root.return_value = self.root
        self.assertEqual((gitlint.git, self.root), gitlint.get_vcs_root())

    def test_get_vcs_hg(self):
        self.git_repository_root.return_value = None
        self.hg_repository_root.return_value = self.root
        self.assertEqual((gitlint.hg, self.root), gitlint.get_vcs_root())

    def test_get_vcs_none(self):
        self.git_repository_root.return_value = None
        self.hg_repository_root.return_value = None
        self.assertEqual((None, None), gitlint.get_vcs_root())
