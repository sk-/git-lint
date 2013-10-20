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
"""Common function used across modules."""

import re


def filter_lines(lines, filter_regex, groups=None):
    """Filters out the lines not matching the pattern.

    Args:
      lines: list[string]: lines to filter.
      pattern: string: regular expression to filter out lines.

    Returns: list[string]: the list of filtered lines.
    """
    pattern = re.compile(filter_regex)
    for line in lines:
        match = pattern.match(line)
        if match:
            if groups is None:
                yield line
            elif len(groups) == 1:
                yield match.group(groups[0])
            else:
                yield tuple(match.group(group) for group in groups)
