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
import io
import os
import shutil
import subprocess
import tempfile
import unittest

import gitlint

# pylint: disable=too-many-public-methods


class E2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_cwd = os.getcwd()
        cls.temp_directory = tempfile.mkdtemp(prefix='gitlint')
        os.chdir(cls.temp_directory)
        subprocess.check_output(['git', 'init'], stderr=subprocess.STDOUT)
        cls.gitlint_config = gitlint.get_config()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_directory, True)
        os.chdir(cls.original_cwd)

    def setUp(self):
        self.out = io.StringIO()

    def test_linters(self):
        for extension, linter_list in self.gitlint_config.items():
            for linter in linter_list:
                self.assert_linter_works(linter.args[0], extension)

    def test_extension_not_defined(self):
        extension = max(self.gitlint_config.keys()) + 'fake'
        filename = os.path.join(self.temp_directory, 'filename' + extension)
        with open(filename, 'w') as f:
            f.write('Foo')
        subprocess.check_output(['git', 'add', filename],
                                stderr=subprocess.STDOUT)
        try:
            output = subprocess.check_output(['git', 'lint'],
                                             stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            self.fail(error.output)
        # Python3 does not like mixing bytes and strings. So we need to convert
        # the first element to unicode first.
        self.assertIn(os.path.relpath(filename).encode('utf-8'), output)
        self.assertIn('SKIPPED'.encode('utf-8'), output)
        self.assertIn(extension.encode('utf-8'), output)

    # TODO(skreft): improves assert so the message is clear in case there's an
    # error. Include output and file that is being processed.
    # TODO(skreft): check that the first file has more than 1 error, check that
    # the second file has 1 new error, check also the lines that changed.
    def assert_linter_works(self, linter_name, extension):
        """Checks that the given linter works well for all the extensions.

        It requires that 3 files are defined:
        - <linter>/original.<extension>: A file with errors
        - <linter>/error.<extension>: New errors are introduced.
        - <linter>/nonewerror.<extension>: A line was modified/added from the
          last file, but no new errors are introduced.
        """
        data_dirname = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'data')
        filename_repo = os.path.join(
            self.temp_directory, '%s%s' % (linter_name, extension))
        filename_original = os.path.join(
            data_dirname, linter_name, 'original%s' % extension)
        filename_error = os.path.join(
            data_dirname, linter_name, 'error%s' % extension)
        filename_nonewerror = os.path.join(
            data_dirname, linter_name, 'nonewerror%s' % extension)

        self.assertTrue(
            os.path.exists(filename_original),
            'You must define file "%s"' % filename_original)
        self.assertTrue(
            os.path.exists(filename_error),
            'You must define file "%s"' % filename_error)
        self.assertTrue(os.path.exists(
            filename_nonewerror),
            'You must define file "%s"' % filename_nonewerror)

        # Add file 1 (original) to repo
        shutil.copy(filename_original, filename_repo)
        subprocess.check_output(['git', 'add', filename_repo],
                                stderr=subprocess.STDOUT)

        # --no-verify is required as a pre-commit hook could be installed.
        subprocess.check_output(
            ['git', 'commit', '-m', 'Commit 1', '--no-verify'],
            stderr=subprocess.STDOUT)

        # Add file 2 (error) to repo
        shutil.copy(filename_error, filename_repo)
        out = io.StringIO()
        response = gitlint.main([], stdout=out, stderr=out)
        if response == 0:
            self.fail(('Git lint for file %s should have failed.\n' +
                       'Output:\n%s') % (filename_error,
                                         out.getvalue()))

        subprocess.check_output(['git', 'add', filename_repo],
                                stderr=subprocess.STDOUT)
        # --no-verify is required as a pre-commit hook could be installed.
        subprocess.check_output(
            ['git', 'commit', '-m', 'Commit 2', '--no-verify'],
            stderr=subprocess.STDOUT)

        # Add file 3 (nonewerror) to repo
        shutil.copy(filename_nonewerror, filename_repo)
        out = io.StringIO()
        response = gitlint.main([], stdout=out, stderr=out)
        if response != 0:
            self.fail(('Git lint for file %s should have not failed. \n' +
                       'Output:\n%s') % (filename_nonewerror,
                                         out.getvalue()))
        subprocess.check_output(['git', 'add', filename_repo],
                                stderr=subprocess.STDOUT)
        subprocess.check_output(['git', 'commit', '-m', 'Commit 3'],
                                stderr=subprocess.STDOUT)
