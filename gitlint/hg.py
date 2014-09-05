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
"""Functions to get information from mercurial."""

import os.path
import subprocess

import gitlint.utils as utils


def repository_root():
    """Returns the root of the repository as an absolute path."""
    try:
        root = subprocess.check_output(['hg', 'root'],
                                       stderr=subprocess.STDOUT).strip()
        # Convert to unicode first
        return root.decode('utf-8')
    except subprocess.CalledProcessError:
        return None


def last_commit():
    """Returns the SHA1 of the last commit."""
    try:
        root = subprocess.check_output(['hg', 'parent', '--template={node}'],
                                       stderr=subprocess.STDOUT).strip()
        # Convert to unicode first
        return root.decode('utf-8')
    except subprocess.CalledProcessError:
        return None


def modified_files(root, tracked_only=False, commit=None):
    """Returns a list of files that has been modified since the last commit.

    Args:
      root: the root of the repository, it has to be an absolute path.
      tracked_only: exclude untracked files when True.
      commit: SHA1 of the commit. If None, it will get the modified files in the
        working copy.

    Returns: a dictionary with the modified files as keys, and additional
      information as value. In this case it adds the status returned by
      hg status.
    """
    assert os.path.isabs(root), "Root has to be absolute, got: %s" % root

    command = ['hg', 'status']
    if commit:
        command.append('--change=%s' % commit)

    # Convert to unicode and split
    status_lines = subprocess.check_output(
        command).decode('utf-8').split(os.linesep)

    modes = ['M', 'A']
    if not tracked_only:
        modes.append(r'\?')
    modes_str = '|'.join(modes)

    modified_file_status = utils.filter_lines(
        status_lines,
        r'(?P<mode>%s) (?P<filename>.+)' % modes_str,
        groups=('filename', 'mode'))

    return dict((os.path.join(root, filename), mode)
                for filename, mode in modified_file_status)


def modified_lines(filename, extra_data, commit=None):
    """Returns the lines that have been modifed for this file.

    Args:
      filename: the file to check.
      extra_data: is the extra_data returned by modified_files. Additionally, a
        value of None means that the file was not modified.
      commit: the complete sha1 (40 chars) of the commit. Note that specifying
        this value will only work (100%) when commit == last_commit (with
        respect to the currently checked out revision), otherwise, we could miss
        some lines.

    Returns: a list of lines that were modified, or None in case all lines are
      new.
    """
    if extra_data is None:
        return []
    if extra_data != 'M':
        return None

    command = ['hg', 'diff', '-U', '0']
    if commit:
        command.append('--change=%s' % commit)
    command.append(filename)

    # Split as bytes, as the output may have some non unicode characters.
    diff_lines = subprocess.check_output(command).split(
        os.linesep.encode('utf-8'))
    diff_line_numbers = utils.filter_lines(
        diff_lines,
        br'@@ -\d+,\d+ \+(?P<start_line>\d+),(?P<lines>\d+) @@',
        groups=('start_line', 'lines'))
    modified_line_numbers = []
    for start_line, lines in diff_line_numbers:
        start_line = int(start_line)
        lines = int(lines)
        modified_line_numbers.extend(range(start_line, start_line + lines))

    return modified_line_numbers
