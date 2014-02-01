#!/bin/python
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
            print 'Error:', error
            return 1
        except:
            print 'Unexpected Error'
            return 2


if __name__ == '__main__':
    sys.exit(lint(sys.argv[1]))
