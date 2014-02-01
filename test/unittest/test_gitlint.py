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
            get_modified_files.assert_called_once_with(root)

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
            get_modified_files.assert_called_once_with(root)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], linters._EXTENSION_TO_LINTER)

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
            get_modified_files.assert_called_once_with(root)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], linters._EXTENSION_TO_LINTER)

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
            get_modified_files.assert_called_once_with(root)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], linters._EXTENSION_TO_LINTER)

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
            get_modified_files.assert_called_once_with(root)
            get_modified_lines.assert_called_once_with('changed.py', ' M')
            lint.assert_called_once_with(
                'changed.py', [3, 14], linters._EXTENSION_TO_LINTER)

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
            expected_calls = [mock.call(root), mock.call(root)]
            self.assertEqual(expected_calls, get_modified_files.call_args_list)
            expected_calls = [mock.call(
                'changed.py', None, linters._EXTENSION_TO_LINTER)] * 2
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
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch(
                'gitlint.git.modified_lines',
                return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint', return_value='OK') as lint:
            self.assertEqual(
                0, gitlint.main(['git-lint', 'changed.py', 'foo.txt']))
            get_modified_files.assert_called_once_with(root)
            expected_calls = [
                mock.call('changed.py', ' M'), mock.call('foo.txt', None)]
            self.assertEqual(expected_calls, get_modified_lines.call_args_list)
            expected_calls = [
                mock.call('changed.py', [3, 14], linters._EXTENSION_TO_LINTER),
                mock.call('foo.txt', [3, 14], linters._EXTENSION_TO_LINTER)]
            self.assertEqual(expected_calls, lint.call_args_list)

    def test_main_with_valid_files_relative(self):
        root = '/home/user/repo'
        with mock.patch('gitlint.git.repository_root', return_value=root), \
             mock.patch('gitlint.find_invalid_filenames', return_value=[]), \
             mock.patch(
                'gitlint.git.modified_files',
                return_value={'changed.py': ' M'}) as get_modified_files, \
             mock.patch(
                'gitlint.git.modified_lines',
                return_value=[3, 14]) as get_modified_lines, \
             mock.patch('gitlint.linters.lint', return_value='OK') as lint:
            self.assertEqual(
                0, gitlint.main(['git-lint', 'bar/../changed.py', './foo.txt']))
            get_modified_files.assert_called_once_with(root)
            expected_calls = [mock.call('changed.py', ' M'),
                              mock.call('foo.txt', None)]
            self.assertEqual(expected_calls, get_modified_lines.call_args_list)
            expected_calls = [
                mock.call('changed.py', [3, 14], linters._EXTENSION_TO_LINTER),
                mock.call('foo.txt', [3, 14], linters._EXTENSION_TO_LINTER)]
            self.assertEqual(expected_calls, lint.call_args_list)
