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
import os.path
import unittest
import sys

import mock
from pyfakefs import fake_filesystem_unittest

import gitlint.utils as utils

# pylint: disable=protected-access


class UtilsTest(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_filter_lines_no_groups(self):
        lines = ['a', 'b', 'c', 'ad']
        self.assertEqual(lines, list(utils.filter_lines(lines, '.')))
        self.assertEqual(['a', 'ad'], list(utils.filter_lines(lines, 'a')))
        self.assertEqual(['ad'], list(utils.filter_lines(lines, '.d')))
        self.assertEqual(['ad'], list(utils.filter_lines(lines, 'd')))
        self.assertEqual([], list(utils.filter_lines(lines, '^d')))
        self.assertEqual([], list(utils.filter_lines(lines, 'foo')))

    def test_filter_lines_one_group(self):
        lines = ['1: foo', '12: bar', '', 'Debug: info']
        self.assertEqual(['1', '12'],
                         list(
                             utils.filter_lines(
                                 lines,
                                 r'(?P<line>\d+): .*',
                                 groups=('line', ))))

    def test_filter_lines_many_groups(self):
        lines = ['1: foo', '12: bar', '', 'Debug: info']
        self.assertEqual([('1', 'foo'), ('12', 'bar')],
                         list(
                             utils.filter_lines(
                                 lines,
                                 r'(?P<line>\d+): (?P<info>.*)',
                                 groups=('line', 'info'))))
        self.assertEqual([('1', 'foo', ':'), ('12', 'bar', ':')],
                         list(
                             utils.filter_lines(
                                 lines,
                                 r'(?P<line>\d+)(?P<separator>:) (?P<info>.*)',
                                 groups=('line', 'info', 'separator'))))

    def test_filter_lines_group_not_always_defined(self):
        lines = ['1: foo', '12: bar', '', 'Debug: info']
        self.assertEqual([('1', None), ('12', None), (None, 'info')],
                         list(
                             utils.filter_lines(
                                 lines,
                                 r'(?P<line>\d+): .*|Debug: (?P<debug>.*)',
                                 groups=('line', 'debug'))))

    def test_filter_lines_group_not_defined(self):
        lines = ['1: foo', '12: bar', '', 'Debug: info']
        self.assertEqual([('1', None), ('12', None)],
                         list(
                             utils.filter_lines(
                                 lines,
                                 r'(?P<line>\d+): .*',
                                 groups=('line', 'debug'))))

    @unittest.skipUnless(sys.version_info >= (3, 5),
                         'pyfakefs does not support pathlib2. See'
                         'https://github.com/jmcgeheeiv/pyfakefs/issues/408')
    def test_open_for_write(self):
        filename = 'foo/bar/new_file'
        with utils._open_for_write(filename) as f:
            f.write('foo')
        with open(filename) as f:
            self.assertEqual('foo', f.read())

    def test_get_cache_filename(self):
        self.fs.create_dir('/abspath')
        os.chdir('/abspath')
        with mock.patch('os.path.expanduser', return_value='/home/user'):
            self.assertEqual(
                '/home/user/.git-lint/cache/linter1/abspath/bar/file.txt',
                utils._get_cache_filename('linter1', 'bar/file.txt'))

            self.assertEqual(
                '/home/user/.git-lint/cache/linter2/abspath/file.txt',
                utils._get_cache_filename('linter2', 'file.txt'))

            self.assertEqual(
                '/home/user/.git-lint/cache/linter3/bar/file.txt',
                utils._get_cache_filename('linter3', '/bar/file.txt'))

    @unittest.skipUnless(sys.version_info >= (3, 5),
                         'pyfakefs does not support pathlib2. See'
                         'https://github.com/jmcgeheeiv/pyfakefs/issues/408')
    def test_save_output_in_cache(self):
        output = 'Some content'
        with mock.patch(
                'gitlint.utils._get_cache_filename',
                return_value='/cache/filename.txt'):
            utils.save_output_in_cache('linter', 'filename', output)

            with open(utils._get_cache_filename('linter', 'filename')) as f:
                self.assertEqual(output, f.read())

    def test_get_output_from_cache_no_cache(self):
        cache_filename = '/cache/filename.txt'
        with mock.patch(
                'gitlint.utils._get_cache_filename',
                return_value=cache_filename):
            self.assertIsNone(
                utils.get_output_from_cache('linter', 'filename'))

    def test_get_output_from_cache_cache_is_expired(self):
        cache_filename = '/cache/filename.txt'
        self.fs.create_file(cache_filename)
        self.fs.create_file('filename')
        with mock.patch(
                'gitlint.utils._get_cache_filename',
                return_value=cache_filename):
            self.assertIsNone(
                utils.get_output_from_cache('linter', 'filename'))

    def test_get_output_from_cache_cache_is_valid(self):
        cache_filename = '/cache/filename.txt'
        content = 'some_content'
        self.fs.create_file('filename')
        self.fs.create_file(cache_filename, contents=content)
        with mock.patch(
                'gitlint.utils._get_cache_filename',
                return_value=cache_filename):
            self.assertEqual(content,
                             utils.get_output_from_cache('linter', 'filename'))

    def test_which_absolute_path(self):
        filename = '/foo/bar.sh'
        self.fs.create_file(filename)
        os.chmod(filename, 0o755)

        self.assertEqual([filename], utils.which(filename))
