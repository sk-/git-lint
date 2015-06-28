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


class E2EBase(object):
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

    def setUp(self):
        self.filename_repo = None

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_directory, True)
        os.chdir(cls.original_cwd)

    def tearDown(self):
        if self.filename_repo is None:
            return

        with open(self.filename_repo, 'w') as f:
            pass
        self.add(self.filename_repo)
        self.commit('Commit teardown')

    def test_extension_not_defined(self):
        extension = '.areallyfakeextension'
        filename = os.path.join(self.temp_directory, 'filename' + extension)
        with open(filename, 'w') as f:
            f.write('Foo')
        self.add(filename)
        response, output = self.lint()
        self.assertEquals(
            0, response, 'Response %s != 0.\nOutput:\n%s' % (response, output))

        self.assertIn(os.path.relpath(filename), output)
        self.assertIn('SKIPPED', output)
        self.assertIn(extension, output)

    def get_linter_output(self, linter_name, file_path):
        cache_path = os.path.expanduser('~/.git-lint/cache')
        filename = os.path.join(cache_path, linter_name, file_path[1:])
        if not os.path.exists(filename):
            return 'No git-lint cache found for %s' % filename

        with open(filename) as f:
            output = f.read()
        return output

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
        self.filename_repo = filename_repo = os.path.join(
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
            ('Git lint for file %s should have failed.\n git-lint output: %s' +
             '\nLinter Output:\n%s') %
            (filename_error,
             output,
             self.get_linter_output(linter_name, filename_repo)))
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

    @classmethod
    def add_linter_check(cls, linter_name, extension):
        """Adds a test for the given linter and extension."""
        def test_linter(self):
            self.assert_linter_works(linter_name, extension)
        test_linter.__name__ = 'test_linter_%s_with_%s' % (linter_name,
                                                           extension[1:])
        setattr(cls, test_linter.__name__, test_linter)

    @classmethod
    def add_linter_checks(cls):
        """Add a test for each defined linter and extension."""
        for extension, linter_list in gitlint.get_config(None).items():
            for linter in linter_list:
                cls.add_linter_check(linter.args[0], extension)


E2EBase.add_linter_checks()


def execute(*args, **kwargs):
    """Executes a command and prints the output in case of error."""
    kwargs['stderr'] = subprocess.STDOUT
    try:
        subprocess.check_output(*args, **kwargs)
    except subprocess.CalledProcessError as error:
        print(error.output)
        raise


class TestGitE2E(E2EBase, unittest.TestCase):
    @classmethod
    def init_repo(cls):
        """Initializes a git repo."""
        execute(['git', 'init'])
        # We need to create a file, otherwise there's no defined branch.
        with open('README', 'w'):
            pass
        cls.add('README')
        cls.commit('Initial commit')

    @staticmethod
    def commit(message):
        """Commit a changeset to the repo.

        The option --no-verify is used as a pre-commit check could be globally
        installed.
        """
        execute(['git', 'commit', '-m', message, '--no-verify'])

    @staticmethod
    def add(filename):
        """Add a file to the repo."""
        execute(['git', 'add', filename])

    def test_submodules(self):
        """Check that repositories with submodules can be handled.

        Checks Issue #62:
          modifying files in a submodule produces an error as it is not possible
          to run git blame on a submodule.
        """
        try:
            original_cwd = os.getcwd()

            submodule_dir = tempfile.mkdtemp(prefix='gitlint')
            os.chdir(submodule_dir)
            self.init_repo()

            repo_dir = tempfile.mkdtemp(prefix='gitlint')
            os.chdir(repo_dir)
            self.init_repo()

            execute(['git', 'submodule', 'add', submodule_dir])
            self.commit('Added submodule')

            submodule_name = os.path.basename(submodule_dir)
            with open(os.path.join(submodule_name, 'LICENSE'), 'w'):
                pass

            self.lint()
        finally:
            os.chdir(original_cwd)
            if submodule_dir:
                shutil.rmtree(submodule_dir)
            if repo_dir:
                shutil.rmtree(repo_dir)


class TestHgE2E(E2EBase, unittest.TestCase):
    @staticmethod
    def init_repo():
        """Initializes a mercurial repo."""
        execute(['hg', 'init'])

    @staticmethod
    def commit(message):
        """Commit a changeset to the repo.

        The environment variable NO_VERIFY=1 is required as a git-lint could be
        installed as pre-commit hook.
        """
        # NO_VERIFY=1 is required as a pre-commit hook could be installed.
        environ = dict(os.environ)
        environ['NO_VERIFY'] = '1'
        execute(['hg', 'commit', '-u', 'onone', '-m', message], env=environ)

    @staticmethod
    def add(filename):
        """Add a file to the repo."""
        execute(['hg', 'add', filename])
