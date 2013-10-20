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
import unittest

import gitlint.utils as utils

# pylint: disable=too-many-public-methods


class UtilsTest(unittest.TestCase):
    def test_filter_lines_no_groups(self):
        lines = ['a', 'b', 'c', 'ad']
        self.assertEqual(lines, list(utils.filter_lines(lines, '.')))
        self.assertEqual(['a', 'ad'], list(utils.filter_lines(lines, 'a')))
        self.assertEqual(['ad'], list(utils.filter_lines(lines, '.d')))
        self.assertEqual([], list(utils.filter_lines(lines, 'd')))
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
