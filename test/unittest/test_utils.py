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

import mock

import gitlint.utils as utils

# pylint: disable=too-many-public-methods


class UtilsTest(unittest.TestCase):
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
        self.assertEqual(
            ['1', '12'],
            list(utils.filter_lines(lines,
                                    r'(?P<line>\d+): .*',
                                    groups=('line',))))

    def test_filter_lines_many_groups(self):
        lines = ['1: foo', '12: bar', '', 'Debug: info']
        self.assertEqual(
            [('1', 'foo'), ('12', 'bar')],
            list(utils.filter_lines(lines,
                                    r'(?P<line>\d+): (?P<info>.*)',
                                    groups=('line', 'info'))))
        self.assertEqual(
            [('1', 'foo', ':'), ('12', 'bar', ':')],
            list(utils.filter_lines(
                lines,
                r'(?P<line>\d+)(?P<separator>:) (?P<info>.*)',
                groups=('line', 'info', 'separator'))))

    def test_filter_lines_group_not_always_defined(self):
        lines = ['1: foo', '12: bar', '', 'Debug: info']
        self.assertEqual(
            [('1', None), ('12', None), (None, 'info')],
            list(utils.filter_lines(lines,
                                    r'(?P<line>\d+): .*|Debug: (?P<debug>.*)',
                                    groups=('line', 'debug'))))

    def test_filter_lines_group_not_defined(self):
        lines = ['1: foo', '12: bar', '', 'Debug: info']
        self.assertEqual(
            [('1', None), ('12', None)],
            list(utils.filter_lines(lines,
                                    r'(?P<line>\d+): .*',
                                    groups=('line', 'debug'))))

    def test_open_for_write(self):
        filename = 'foo/bar/new_file'
        with mock.patch('io.open',
                        mock.mock_open(),
                        create=True) as mock_open, \
             mock.patch.object(
                utils.pathlib.Path,
                'mkdir',
                return_value=True) as mock_create:
            utils._open_for_write(filename)

            mock_create.assert_called_once_with(
                parents=True,
                exist_ok=True)
            mock_open.assert_called_once_with(filename, 'w')

    def test_get_cache_filename(self):
        def mock_abspath(filename):
            if os.path.isabs(filename):
                return filename
            return '/foo/%s' % filename

        with mock.patch('os.path.abspath',
                        side_effect=mock_abspath), \
             mock.patch('os.path.expanduser',
                        side_effect=lambda a: '/home/user'):
            self.assertEqual(
                '/home/user/.git-lint/cache/linter1/foo/bar/file.txt',
                utils._get_cache_filename('linter1', 'bar/file.txt'))

            self.assertEqual(
                '/home/user/.git-lint/cache/linter2/foo/file.txt',
                utils._get_cache_filename('linter2', 'file.txt'))

            self.assertEqual(
                '/home/user/.git-lint/cache/linter3/bar/file.txt',
                utils._get_cache_filename('linter3', '/bar/file.txt'))

    def test_save_output_in_cache(self):
        output = 'Some content'
        cache_filename = '/cache/filename.txt'
        mock_file = mock.MagicMock()
        with mock.patch('gitlint.utils._get_cache_filename',
                        return_value=cache_filename), \
             mock.patch('gitlint.utils._open_for_write',
                        mock.mock_open(mock_file)) as mock_open:
            utils.save_output_in_cache('linter', 'filename', output)
            mock_open.assert_called_once_with(cache_filename)
            mock_file().write.assert_called_once_with(output)

    def test_get_output_from_cache_no_cache(self):
        cache_filename = '/cache/filename.txt'
        with mock.patch('gitlint.utils._get_cache_filename',
                        return_value=cache_filename), \
             mock.patch('os.path.exists', return_value=False):
            self.assertIsNone(
                utils.get_output_from_cache('linter', 'filename'))

    def test_get_output_from_cache_cache_is_expired(self):
        cache_filename = '/cache/filename.txt'
        with mock.patch('gitlint.utils._get_cache_filename',
                        return_value=cache_filename), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.getmtime', side_effect=[2, 1]):
            self.assertIsNone(
                utils.get_output_from_cache('linter', 'filename'))

    def test_get_output_from_cache_cache_is_valid(self):
        cache_filename = '/cache/filename.txt'
        content = 'some_content'
        with mock.patch('gitlint.utils._get_cache_filename',
                        return_value=cache_filename), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.path.getmtime', side_effect=[1, 2]), \
             mock.patch('io.open',
                        mock.mock_open(read_data=content),
                        create=True) as mock_open:
            self.assertEqual(
                content, utils.get_output_from_cache('linter', 'filename'))
            mock_open.assert_called_once_with(cache_filename)

    def test_which_absolute_path(self):
        with mock.patch('os.path.isfile', return_value=True), \
            mock.patch('os.access', return_value=True):
            filename = '/foo/bar.sh'
            self.assertEqual([filename], utils.which(filename))
