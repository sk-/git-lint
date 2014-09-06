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


class TestGitE2E(unittest.TestCase):
    @staticmethod
    def init_repo():
        """Initializes a git repo."""
        subprocess.check_output(['git', 'init'], stderr=subprocess.STDOUT)

    @staticmethod
    def commit(message):
        """Commit a changeset to the repo.

        The option --no-verify is used as a pre-commit check could be globally
        installed.
        """
        subprocess.check_output(
            ['git', 'commit', '-m', message, '--no-verify'],
            stderr=subprocess.STDOUT)

    @staticmethod
    def add(filename):
        """Add a file to the repo."""
        subprocess.check_output(['git', 'add', filename],
                                stderr=subprocess.STDOUT)

    @staticmethod
    def lint():
        """Returns the response and ouput of git-lint."""
        out = io.StringIO()
        response = gitlint.main([], stdout=out, stderr=out)

        return response, out.getvalue()

    @classmethod
    def setUpClass(cls):
        cls.original_cwd = os.getcwd()
        cls.temp_directory = tempfile.mkdtemp(prefix='gitlint')
        os.chdir(cls.temp_directory)
        cls.init_repo()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_directory, True)
        os.chdir(cls.original_cwd)

    def setUp(self):
        self.out = io.StringIO()

    @classmethod
    def add_linter_e2echeck(cls, linter_name, extension):
        """Adds a test for the given linter and extension."""
        def test_linter(self):
            self.assert_linter_works(linter_name, extension)
        test_linter.__name__ = 'test_linter_%s_with_%s' % (linter_name,
                                                           extension[1:])
        setattr(cls, test_linter.__name__, test_linter)

    def test_extension_not_defined(self):
        extension = '.areallyfakeextension'
        filename = os.path.join(self.temp_directory, 'filename' + extension)
        with open(filename, 'w') as f:
            f.write('Foo')
        self.add(filename)
        response, output = self.lint()
        self.assertEquals(
            0, response, 'Response %s != 0.\nOutput:\n%s' % (response, output))

        # Python3 does not like mixing bytes and strings. So we need to convert
        # the first element to unicode first.
        self.assertIn(os.path.relpath(filename).encode('utf-8'), output)
        self.assertIn('SKIPPED'.encode('utf-8'), output)
        self.assertIn(extension.encode('utf-8'), output)

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
        self.add(filename_repo)
        self.commit('Commit 1')

        # Add file 2 (error) to repo
        shutil.copy(filename_error, filename_repo)
        response, output = self.lint()
        self.assertNotEquals(
            0, response,
            ('Git lint for file %s should have failed.\n Output:\n%s') %
            (filename_error, output))
        self.add(filename_repo)
        self.commit('Commit 2')

        # Add file 3 (nonewerror) to repo
        shutil.copy(filename_nonewerror, filename_repo)
        response, output = self.lint()
        self.assertEquals(
            0, response,
            ('Git lint for file %s should have not failed. \nOutput:\n%s') %
            (filename_nonewerror, output))
        self.add(filename_repo)
        self.commit('Commit 3')


def populate_linter_checks():
    """Add a test for each defined linter and extension."""
    for extension, linter_list in gitlint.get_config(None).items():
        for linter in linter_list:
            TestGitE2E.add_linter_e2echeck(linter.args[0], extension)


populate_linter_checks()


class TestHgE2E(TestGitE2E):
    @staticmethod
    def init_repo():
        """Initializes a mercurial repo."""
        subprocess.check_output(['hg', 'init'], stderr=subprocess.STDOUT)

    @staticmethod
    def commit(message):
        """Commit a changeset to the repo.

        The environment variable NO_VERIFY=1 is required as a git-lint could be
        installed as pre-commit hook.
        """
        # NO_VERIFY=1 is required as a pre-commit hook could be installed.
        environ = dict(os.environ)
        environ['NO_VERIFY'] = '1'
        subprocess.check_output(
            ['hg', 'commit', '-m', message],
            stderr=subprocess.STDOUT,
            env=environ)

    @staticmethod
    def add(filename):
        """Add a file to the repo."""
        subprocess.check_output(['hg', 'add', filename],
                                stderr=subprocess.STDOUT)
