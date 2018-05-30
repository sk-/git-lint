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
import subprocess
import unittest

import mock

import gitlint.hg as hg

# pylint: disable=too-many-public-methods


class HgTest(unittest.TestCase):
    @mock.patch('subprocess.check_output', return_value=b'/home/user/repo\n')
    def test_repository_root_ok(self, check_output):
        self.assertEqual('/home/user/repo', hg.repository_root())
        check_output.assert_called_once_with(
            ['hg', 'root'], stderr=subprocess.STDOUT)

    @mock.patch('subprocess.check_output')
    def test_repository_root_error(self, check_output):
        check_output.side_effect = subprocess.CalledProcessError(255, '', '')
        self.assertEqual(None, hg.repository_root())

    @mock.patch('subprocess.check_output')
    def test_modified_files(self, check_output):
        check_output.return_value = os.linesep.join([
            'A docs/file1.txt', 'M data/file2.json', 'R file3.py',
            'C file4.js', '! file5.txt', '? untracked.txt', 'I ignored.txt',
            '  origin.txt'
        ]).encode('utf-8')

        self.assertEqual({
            '/home/user/repo/docs/file1.txt': 'A',
            '/home/user/repo/data/file2.json': 'M',
            '/home/user/repo/untracked.txt': '?'
        }, hg.modified_files('/home/user/repo'))
        check_output.assert_called_once_with(['hg', 'status'])

    @mock.patch('subprocess.check_output')
    def test_modified_files_tracked_only(self, check_output):
        check_output.return_value = os.linesep.join([
            'A docs/file1.txt', 'M data/file2.json', 'R file3.py',
            'C file4.js', '! file5.txt', '? untracked.txt', 'I ignored.txt',
            '  origin.txt'
        ]).encode('utf-8')

        self.assertEqual({
            '/home/user/repo/docs/file1.txt': 'A',
            '/home/user/repo/data/file2.json': 'M'
        }, hg.modified_files('/home/user/repo', tracked_only=True))
        check_output.assert_called_once_with(['hg', 'status'])

    @mock.patch('subprocess.check_output', return_value=b'')
    def test_modified_files_nothing_changed(self, check_output):
        self.assertEqual({}, hg.modified_files('/home/user/repo'))
        check_output.assert_called_once_with(['hg', 'status'])

    @mock.patch('subprocess.check_output')
    def test_modified_files_with_commit(self, check_output):
        check_output.return_value = os.linesep.join([
            'A docs/file1.txt', 'M data/file2.json', 'R file3.py',
            'C file4.js', '! file5.txt', '? untracked.txt', 'I ignored.txt',
            '  origin.txt'
        ]).encode('utf-8')
        commit = '012012012012'

        self.assertEqual({
            '/home/user/repo/docs/file1.txt': 'A',
            '/home/user/repo/data/file2.json': 'M',
            '/home/user/repo/untracked.txt': '?'
        }, hg.modified_files('/home/user/repo', commit=commit))
        check_output.assert_called_once_with(
            ['hg', 'status', '--change=%s' % commit])

    def test_modified_files_non_absolute_root(self):
        with self.assertRaises(AssertionError):
            hg.modified_files('foo/bar')

    @mock.patch('subprocess.check_output')
    def test_modified_lines(self, check_output):
        check_output.return_value = os.linesep.join([
            '--- a/foo/bar/a.py',
            '+++ b/foo/bar/a.py',
            '@@ -200,0 +201,2 @@ class Test:',
            '+        import pprint',
            '+        pprint.pprint(foo)',
            '@@ -400,0 +401,0 @@ class Test:',
            '@@ -600,0 +601,1 @@ class Test:',
            '+        import pprint',
        ]).encode('utf-8')

        self.assertEqual([201, 202, 601],
                         list(
                             hg.modified_lines('/home/user/repo/foo/bar.txt',
                                               'M')))
        check_output.assert_called_once_with(
            ['hg', 'diff', '-U', '0', '/home/user/repo/foo/bar.txt'])

    @mock.patch('subprocess.check_output')
    def test_modified_lines_with_commit(self, check_output):
        check_output.return_value = os.linesep.join([
            '--- a/foo/bar/a.py',
            '+++ b/foo/bar/a.py',
            '@@ -200,0 +201,2 @@ class Test:',
            '+        import pprint',
            '+        pprint.pprint(foo)',
            '@@ -400,0 +401,0 @@ class Test:',
            '@@ -600,0 +601,1 @@ class Test:',
            '+        import pprint',
        ]).encode('utf-8')
        commit = '0123' * 10

        self.assertEqual([201, 202, 601],
                         list(
                             hg.modified_lines(
                                 '/home/user/repo/foo/bar.txt',
                                 'M',
                                 commit=commit)))
        check_output.assert_called_once_with([
            'hg', 'diff', '-U', '0',
            '--change=%s' % commit, '/home/user/repo/foo/bar.txt'
        ])

    def test_modified_lines_new_addition(self):
        self.assertEqual(None,
                         hg.modified_lines('/home/user/repo/foo/bar.txt', 'A'))

    def test_modified_lines_untracked(self):
        self.assertEqual(None,
                         hg.modified_lines('/home/user/repo/foo/bar.txt', '?'))

    def test_modified_lines_no_info(self):
        self.assertEqual([],
                         list(
                             hg.modified_lines('/home/user/repo/foo/bar.txt',
                                               None)))

    @mock.patch('subprocess.check_output', return_value=b'0a' * 20 + b'\n')
    def test_last_commit(self, check_output):
        self.assertEqual('0a' * 20, hg.last_commit())
        check_output.assert_called_once_with(
            ['hg', 'parent', '--template={node}'], stderr=subprocess.STDOUT)

    @mock.patch('subprocess.check_output')
    def test_last_commit_not_in_repo(self, check_output):
        check_output.side_effect = subprocess.CalledProcessError(255, '', '')
        self.assertEqual(None, hg.last_commit())
