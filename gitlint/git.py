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
"""Functions to get information from git."""

import os.path
import subprocess

import gitlint.utils as utils


def repository_root():
    """Returns the root of the repository as an absolute path."""
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                       stderr=subprocess.STDOUT).strip()
        return root
    except subprocess.CalledProcessError:
        return None


def modified_files(root):
    """Returns a list of files that has been modified since the last commit.

    Args:
      root: the root of the repository, it has to be an absolute path.

    Returns: a dictionary with the modified files as keys, and additional
      information as value. In this case it adds the status returned by
      git status.
    """
    assert os.path.isabs(root), "Root has to be absolute, got: %s" % root

    # TODO(skreft): add '--untracked-files=no'?
    status_lines = subprocess.check_output(
        ['git', 'status', '--porcelain',
         '--untracked-files=all']).split(os.linesep)
    modified_file_status = utils.filter_lines(
        status_lines,
        r'(?P<mode>M | M|A |\?\?|AM) (?P<filename>.+)',
        groups=('filename', 'mode'))

    return dict((os.path.join(root, filename), mode)
                for filename, mode in modified_file_status)


def modified_lines(filename, extra_data):
    """Returns the lines that have been modifed for this file.

    Args:
      filename: the file to check.
      extra_data: is the extra_data returned by modified_files. Additionally, a
        value of None means that the file was not modified.

    Returns: a list of lines that were modified, or None in case all lines are
      new.
    """
    if extra_data is None:
        return []
    if extra_data not in ('M ', ' M'):
        return None
    blame_lines = subprocess.check_output(
        ['git', 'blame', '--porcelain', filename]).split(os.linesep)
    modified_line_numbers = utils.filter_lines(
        blame_lines,
        r'0000000000000000000000000000000000000000 (?P<line>\d+) (\d+)',
        groups=('line',))

    return map(int, modified_line_numbers)
