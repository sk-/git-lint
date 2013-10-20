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
import os
import subprocess
import unittest

import mock

import gitlint.git as git

# pylint: disable=too-many-public-methods


class GitTest(unittest.TestCase):
    def test_repository_root_ok(self):
        with mock.patch('subprocess.check_output',
                        return_value='/home/user/repo'):
            self.assertEqual('/home/user/repo', git.repository_root())

    def test_repository_root_error(self):
        with mock.patch('subprocess.check_output',
                        side_effect=subprocess.CalledProcessError(1, '', '')):
            self.assertEqual(None, git.repository_root())

    def test_modified_files(self):
        output = os.linesep.join(['A  docs/file1.txt',
                                  'M  data/file2.json',
                                  'D  file3.py',
                                  '?? file4.js'])
        original_relpath = os.path.relpath
        with mock.patch('subprocess.check_output',
                        return_value=output), \
             mock.patch('os.path.relpath',
                        side_effect=lambda fname: original_relpath(
                            fname, '/home/user/repo/data')):
            self.assertEqual(
                {'../docs/file1.txt': 'A ',
                 'file2.json': 'M ',
                 '../file4.js': '??'},
                git.modified_files('/home/user/repo'))

    def test_modified_files_nothing_changed(self):
        output = ''
        original_relpath = os.path.relpath
        with mock.patch('subprocess.check_output',
                        return_value=output), \
             mock.patch('os.path.relpath',
                        side_effect=lambda fname: original_relpath(
                            fname, '/home/user/repo/data')):
            self.assertEqual({}, git.modified_files('/home/user/repo'))

    def test_modified_lines(self):
        output = os.linesep.join([
            'baz',
            '0000000000000000000000000000000000000000 2 2 4',
            'foo',
            '0000000000000000000000000000000000000000 5 5',
            'bar'])
        with mock.patch('subprocess.check_output',
                        return_value=output) as check_output:
            self.assertEqual(
                [2, 5],
                git.modified_lines('/home/user/repo/foo/bar.txt', ' M'))
            self.assertEqual(
                [2, 5],
                git.modified_lines('/home/user/repo/foo/bar.txt', 'M '))
            expected_calls = [mock.call(
                ['git', 'blame', '--porcelain',
                 '/home/user/repo/foo/bar.txt'])] * 2
            self.assertEqual(expected_calls, check_output.call_args_list)

    def test_modified_lines_new_addition(self):
        self.assertEqual(
            None,
            git.modified_lines('/home/user/repo/foo/bar.txt', 'A '))

    def test_modified_lines_untracked(self):
        self.assertEqual(
            None,
            git.modified_lines('/home/user/repo/foo/bar.txt', '??'))

    def test_modified_lines_no_info(self):
        self.assertEqual(
            [],
            git.modified_lines('/home/user/repo/foo/bar.txt', None))
