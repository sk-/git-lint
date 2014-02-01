#!/bin/python
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
"""Simple YAML linter."""
import sys

import yaml


def lint(filename):
    """Lints a YAML file, returning 0 in case of success."""
    with open(filename) as f:
        try:
            yaml.load(f)
            return 0
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
            print('Error: %s' % error)
            return 1
        except:
            print('Unexpected Error')
            return 2


if __name__ == '__main__':
    sys.exit(lint(sys.argv[1]))
