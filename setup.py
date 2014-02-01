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

from setuptools import setup, find_packages

setup(name='git-lint',
      version='0.0.3',
      description='Git Lint',
      long_description=open('README.rst').read(),
      author='Sebastian Kreft',
      url='http://github.com/sk-/git-lint',
      packages=find_packages(exclude=['test']),
      package_dir={'gitlint': 'gitlint'},
      package_data={'gitlint': ['*.yaml']},
      scripts=[
          'scripts/git-lint',
          'scripts/custom_linters/ini_linter.py',
          'scripts/custom_linters/yaml_linter.py',
          'scripts/custom_linters/jpegtran-linter.sh',
          'scripts/custom_linters/optipng-linter.sh',
          'scripts/custom_linters/pngcrush-linter.sh',
      ],
      install_requires=['nose', 'mock', 'pyyaml', 'termcolor', 'docopt'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: Unix',
          'Programming Language :: Python :: 2',
          'Topic :: Software Development :: Version Control',
      ],
     )
