#!/usr/bin/env python
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

import ast
import io
import os
from setuptools import setup, find_packages

version_file = open(os.path.join('gitlint', 'version.py'))

version = version_file.read()
version = ast.literal_eval(version.rsplit('=', 1)[1].strip())

setup(
    name='git-lint',
    version=version,
    description='Git Lint',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    author='Sebastian Kreft',
    url='http://github.com/sk-/git-lint',
    packages=find_packages(exclude=['test']),
    package_dir={'gitlint': 'gitlint'},
    package_data={'gitlint': ['configs/*'], '': ['README.rst', 'LICENSE']},
    scripts=[
        'scripts/git-lint',
        'scripts/pre-commit.git-lint.sh',
        'scripts/pre-commit.hg-lint.sh',
        'scripts/custom_linters/ini_linter.py',
        'scripts/custom_linters/jpegtran-linter.sh',
        'scripts/custom_linters/optipng-linter.sh',
        'scripts/custom_linters/pngcrush-linter.sh',
        'scripts/custom_linters/tidy-wrapper.sh',
    ],
    install_requires=[
        'pyyaml',
        'termcolor',
        'docopt',
        # Packages specific to linters. They are optional, but to ease the use
        # we prefer to put them here.
        'html-linter',
        'template-remover',
        'docutils',
        'pathlib2',
    ],
    tests_require=['nose>=1.3', 'mock'],
    extras_require={
        ':python_version == "2.7"': ['futures']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Version Control',
    ],
)
