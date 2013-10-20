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
import os.path
import subprocess

import gitlint.utils as utils


def repository_root():
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                       stderr=subprocess.STDOUT).strip()
        return root
    except subprocess.CalledProcessError:
        return None


def modified_files(root):
    # TODO(skreft): add '--untracked-files=no'?
    status_lines = subprocess.check_output(
        ['git', 'status', '--porcelain', '--untracked-files=no']).split(os.linesep)
    modified_files = utils.filter_lines(
        status_lines,
        r'(?P<mode>M | M|A |\?\?) (?P<filename>.+)',
        groups=('filename', 'mode'))

    return dict((os.path.relpath(os.path.join(root, filename)), mode)
                for filename, mode in modified_files)


def modified_lines(filename, extra_data):
    if extra_data is None:
        return []
    if extra_data not in ('M ', ' M'):
        return None
    blame_lines = subprocess.check_output(
        ['git', 'blame', '--porcelain', filename]).split(os.linesep)
    modified_lines = utils.filter_lines(
        blame_lines,
        r'0000000000000000000000000000000000000000 (?P<line>\d+) (\d+)',
        groups=('line',))

    return map(int, modified_lines)
