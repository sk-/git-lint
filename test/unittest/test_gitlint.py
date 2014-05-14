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

import os
import sys
import unittest

import mock

import gitlint
import gitlint.linters as linters

# pylint: disable=too-many-public-methods


class GitLintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._stderr = sys.stderr
        sys.stderr = sys.stdout

    @classmethod
    def tearDownClass(cls):
        sys.stderr = cls._stderr

    def test_find_invalid_filenames(self):
        root = '/home/user/repo'
        filenames = ['/tmp/outside_repo',
                     '%s/inexistent_file' % root,
                     '%s/directory_in_repo/' % root,
                     '%s/valid' % root]
        expected = {
            '/tmp/outside_repo': 'does not belong to repository',
            '%s/inexistent_file' % root: 'does not exist',
            '%s/directory_in_repo/' % root: 'Directories are not yet supported',
        }

        with mock.patch(
                'os.path.exists',
                side_effect=lambda filename: 'inexistent' not in filename), \
             mock.patch(
                'os.path.isdir',
                side_effect=lambda filename: 'directory' in filename):
            invalid_filenames = dict(
                gitlint.find_invalid_filenames(filenames, root))

        self.assertEqual(expected.keys(), invalid_filenames.keys())
        for filename in invalid_filenames:
            self.assertIn(filename, invalid_filenames[filename])
            self.assertIn(expected[filename], invalid_filenames[filename])

    def test_main_not_in_repo(self):
        with mock.patch('gitlint.git.repository_root', return_value=None):
            self.assertEqual(128, gitlint.main([]))

    def test_main_nothing_changed(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch('gitlint.git.modified_files',
                        return_value={}) as get_modified_files:
            self.assertEqual(0, gitlint.main([]))
            get_modified_files.assert_called_once_with(root, tracked_only=False)

    def test_main_file_changed_and_still_valid(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch('gitlint.git.modified_lines',
                        return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint', return_value='OK') as lint:
            self.assertEqual(0, gitlint.main([]))
            get_modified_files.assert_called_once_with(root, tracked_only=False)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], gitlint.get_config())

    def test_main_file_changed_and_still_valid_tracked_only(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch('gitlint.git.modified_lines',
                        return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint', return_value='OK') as lint:
            self.assertEqual(0, gitlint.main(['git-lint', '-t']))
            self.assertEqual(0, gitlint.main(['git-lint', '--tracked']))
            expected_calls = [mock.call(root, tracked_only=True)] * 2
            self.assertEqual(expected_calls, get_modified_files.call_args_list)
            expected_calls = [mock.call(
                'changed.py', [3, 14], gitlint.get_config())] * 2
            self.assertEqual(expected_calls, lint.call_args_list)
            expected_calls = [mock.call('changed.py', ' M')] * 2
            self.assertEqual(expected_calls, get_modified_lines.call_args_list)

    def test_main_file_changed_but_skipped(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch(
                'gitlint.git.modified_lines',
                return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint',
                        return_value='SKIPPED: foo') as lint:
            self.assertEqual(0, gitlint.main([]))
            get_modified_files.assert_called_once_with(root, tracked_only=False)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], gitlint.get_config())

    def test_main_file_linter_not_found(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch(
                'gitlint.git.modified_lines',
                return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint',
                        return_value='ERROR: foo') as lint:
            self.assertEqual(4, gitlint.main([]))
            get_modified_files.assert_called_once_with(root, tracked_only=False)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], gitlint.get_config())

    def test_main_file_changed_and_now_invalid(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch(
                'gitlint.git.modified_lines',
                return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint',
                        return_value='3: Error') as lint:
            self.assertEqual(1, gitlint.main([]))
            get_modified_files.assert_called_once_with(root, tracked_only=False)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], gitlint.get_config())

    def test_main_force_all_lines(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch('gitlint.linters.lint',
                        return_value='3: Error') as lint:
            self.assertEqual(1, gitlint.main(['git-lint', '--force']))
            self.assertEqual(1, gitlint.main(['git-lint', '-f']))
            expected_calls = [mock.call(root, tracked_only=False)] * 2
            self.assertEqual(expected_calls, get_modified_files.call_args_list)
            expected_calls = [mock.call(
                'changed.py', None, gitlint.get_config())] * 2
            self.assertEqual(expected_calls, lint.call_args_list)

    def test_main_with_invalid_files(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch('gitlint.find_invalid_filenames',
                        return_value=[('foo.txt', 'does not exist')]):
            self.assertEqual(2, gitlint.main(['git-lint', 'foo.txt']))

    def test_main_with_valid_files(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch('gitlint.find_invalid_filenames', return_value=[]), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={
                    '/home/user/repo/changed.py': ' M'
                }) as get_modified_files, \
             mock.patch(
                'gitlint.git.modified_lines',
                return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint', return_value='OK') as lint, \
             mock.patch('os.getcwd', return_value=root):
            self.assertEqual(
                0, gitlint.main(['git-lint', 'changed.py', 'foo.txt']))
            get_modified_files.assert_called_once_with(root, tracked_only=False)
            expected_calls = [
                mock.call('/home/user/repo/changed.py', ' M'),
                mock.call('/home/user/repo/foo.txt', None),
            ]
            self.assertEqual(expected_calls, get_modified_lines.call_args_list)
            expected_calls = [
                mock.call('/home/user/repo/changed.py',
                          [3, 14],
                          gitlint.get_config()),
                mock.call('/home/user/repo/foo.txt',
                          [3, 14],
                          gitlint.get_config())]
            self.assertEqual(expected_calls, lint.call_args_list)

    def test_main_with_valid_files_relative(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch('gitlint.find_invalid_filenames', return_value=[]), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={
                    '/home/user/repo/changed.py': ' M'
                }) as get_modified_files, \
             mock.patch(
                'gitlint.git.modified_lines',
                return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint', return_value='OK') as lint, \
             mock.patch('os.getcwd', return_value=root):
            self.assertEqual(
                0, gitlint.main(['git-lint', 'bar/../changed.py', './foo.txt']))
            get_modified_files.assert_called_once_with(root, tracked_only=False)
            expected_calls = [mock.call('/home/user/repo/changed.py', ' M'),
                              mock.call('/home/user/repo/foo.txt', None)]
            self.assertEqual(expected_calls, get_modified_lines.call_args_list)
            expected_calls = [
                mock.call('/home/user/repo/changed.py',
                          [3, 14],
                          gitlint.get_config()),
                mock.call('/home/user/repo/foo.txt',
                          [3, 14],
                          gitlint.get_config())]
            self.assertEqual(expected_calls, lint.call_args_list)

    def test_get_config(self):
        root = '/home/user/repo'
        git_config = os.path.join(root, '.gitlint.yaml')
        base_config = os.path.join(os.path.join(
            os.path.dirname(gitlint.__file__), 'configs', 'config.yaml'))
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

        with mock.patch('gitlint.git.repository_root', return_value=root), \
            mock.patch('os.path.exists', return_value=True), \
            mock.patch('gitlint.open',
                       mock.mock_open(read_data=config),
                       create=True) as mock_open:
            parsed_config = gitlint.get_config()
            mock_open.assert_called_once_with(git_config)
            self.assertIn('.py', parsed_config)

        with mock.patch('gitlint.git.repository_root', return_value=root), \
            mock.patch('os.path.exists', return_value=False), \
            mock.patch('gitlint.open',
                       mock.mock_open(read_data=config),
                       create=True) as mock_open:
            parsed_config = gitlint.get_config()
            mock_open.assert_called_once_with(base_config)
            self.assertIn('.py', parsed_config)

        # When not in a repo should return the default config.
        with mock.patch('gitlint.git.repository_root', return_value=None), \
            mock.patch('os.path.exists', return_value=False), \
            mock.patch('gitlint.open',
                       mock.mock_open(read_data=config),
                       create=True) as mock_open:
            parsed_config = gitlint.get_config()
            mock_open.assert_called_once_with(base_config)
            self.assertIn('.py', parsed_config)

        # When config file is empty return an empty dictionary.
        with mock.patch('gitlint.git.repository_root', return_value=root), \
            mock.patch('os.path.exists', return_value=True), \
            mock.patch('gitlint.open',
                       mock.mock_open(read_data=''),
                       create=True) as mock_open:
            parsed_config = gitlint.get_config()
            mock_open.assert_called_once_with(git_config)
            self.assertEquals({}, parsed_config)
