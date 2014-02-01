#!/bin/python
"""Simple INI linter."""
import ConfigParser
import sys


def lint(filename):
    """Lints an INI file, returning 0 in case of success."""
    config = ConfigParser.ConfigParser()
    try:
        config.read(filename)
        return 0
    except ConfigParser.Error as error:
        print 'Error:', error
        return 1
    except:
        print 'Unexpected Error'
        return 2


if __name__ == '__main__':
    sys.exit(lint(sys.argv[1]))
