Git-Lint
========

.. image:: https://badge.fury.io/py/git-lint.png
    :target: http://badge.fury.io/py/git-lint

.. image:: https://travis-ci.org/sk-/git-lint.png?branch=master
    :target: https://travis-ci.org/sk-/git-lint

.. image:: https://coveralls.io/repos/sk-/git-lint/badge.png?branch=master
    :target: https://coveralls.io/r/sk-/git-lint?branch=master

Git-lint is a tool for improving source code one step at a time.

Motivation
----------

Often times enforcing coding styles to an existing project can be a nightmare.
Some reasons may include:

* the codebase is already a mess and the output of the tools is overwhelming.
* developers don't feel confident changing lines they do not own.
* or they just don't know what tool to use.

Features
--------

This tool tackles all the 3 problems mentioned above by providing just a single
tool that lints all the modified files. For each filetype it may use even more
than one linter or tool. Furthermore by default it only report problems of lines
that were added or modified.

Current linters:

- CSS

  * `Csslint <https://github.com/stubbornella/csslint>`_

- SCSS

  * `scss-lint <https://github.com/causes/scss-lint>`_

- Python

  * `Pylint <http://www.pylint.org/>`_
  * `PEP8 <https://pypi.python.org/pypi/pep8/1.4.6>`_

- PHP

  * `Php Code Sniffer <http://pear.php.net/package/PHP_CodeSniffer/>`_

- Javascript

  * `Jshint <http://www.jshint.com/>`_
  * `Gjslint <https://developers.google.com/closure/utilities/>`_

- JPEG

  * Custom via `Jpegtran <http://manpages.ubuntu.com/manpages/raring/man1/jpegtran.1.html>`_

- PNG

  * Custom via `Pngcrush <http://manpages.ubuntu.com/manpages/raring/man1/pngcrush.1.html>`_
  * Custom via `Optipng <http://manpages.ubuntu.com/manpages/raring/man1/optipng.1.html>`_

- RST

  * Via `rst2html.py (docutils) <http://docs.python.org/2/library/json.html>`_

- JSON

  * Via python `json.tool module <http://docs.python.org/2/library/json.html>`_

- YAML

  * Custom via `PyYAML <http://pyyaml.org/>`_

- INI

  * Custom via `ConfigParser module <http://docs.python.org/2/library/configparser.html>`_

- HTML

  * `HTML-Linter <https://github.com/deezer/html-linter>`_
  * `Tidy <https://w3c.github.io/tidy-html5/>`_ with preprocessing from `template-remover <https://github.com/deezer/html-linter>`_

- Ruby

  * `ruby-lint <https://github.com/yorickpeterse/ruby-lint>`_
  * `rubocop <https://github.com/bbatsov/rubocop>`_

- Java

  * `PMD <http://pmd.sourceforge.net/>`_ (it requires to put the script run.sh in your PATH)
  * `Checkstyle <http://checkstyle.sourceforge.net/>`

Example use
-----------

Below is the simplest call, for a detailed list, see the help::

  $ git lint
  Linting file: src/html/main.js
  Line 13, E:0110: Line too long (328 characters).
  Line 31, E:0001: Extra space at end of line
  src/html/main.js: line 75, col 11, ['location'] is better written in dot notation.

  Linting file: src/html/main.css
  src/html/main.css: line 1, col 135, Warning - Duplicate property 'margin' found.

  Linting file: api.py
  api.py:6: [C0301(line-too-long), ] Line too long (87/80)
  api.py:6: [R0913(too-many-arguments), callMethod] Too many arguments (6/5)
  api.py:6: [C0103(invalid-name), callMethod] Invalid function name "callMethod"


By default git lint only reports problems with the modified lines
(with the exception of some linters that check that the whole file is sound).
To force displaying all the output from the linters use the -f option.

Installation
------------

You can install, upgrade or uninstall git-lint with these commands::

  $ pip install git-lint
  $ pip install --upgrade git-lint
  $ pip uninstall git-lint

Configuration
-------------

Git-lint comes with a default configuration that includes all the linters listed
above. If you don't like that list you can write your own configuration and put
it in a file called `.gitlint.yaml` in the root of your repository. You can copy
the file https://github.com/sk-/git-lint/blob/master/gitlint/configs/config.yaml
to your repo and modify it.

If you add a new linter or add a new flag to any of the commands, please
share that with us, so we can integrate those changes.

The configuration support two variables for the command, requirements and
arguments:

* %(REPO_HOME)s: the root of your repo.
* %(DEFAULT_CONFIGS)s: the location of the default config files.

Python Versions
---------------

Python 2.7 is supported, and it should also work for Python 3.2, 3.3 and 3.4.
Python 2.6 is not supported because of the lack of subprocess.check_output.

Development
-----------

Help for this project is more than welcomed, so feel free to create an issue or
to send a pull request via http://github.com/sk-/git-lint.

Tests are run using nose, either with::

  $ python setup.py nosetests
  $ nosetests

This same tool is run for every commit, so errors and style problems are caught
early.

Adding a linter
---------------
Just need to configure the file gitlint/config.yaml. I hope the syntax is self
explanatory. (Note to myself: don't be so lazy and write a proper doc for this.)

TODOS and Possible Features
---------------------------

* Add travis-ci configuration for e2e tests.
* Support directories as arguments
* Provide a man page so 'git help lint' and 'git lint --help' work. I already
  have a script for converting the Usage to a man page, but I still need to
  figure out how to install it on the system.
* Allow to run a command or function when setting up the linter? These can be
  achieved now by running a bash script wrapping the linter. The rationale for
  this is that some linters, like jshint, only allow options to be in a
  configuration file. This is done at the moment via scripts present in the
  folder linters.
* Decide what linter to use based on the whole filename or even in the filetype,
  as returned by the command file.
* Provide better options for colorizing the output, and maybe a way to disable
  it. Also detect if colors are supported or if it is a tty.
* Add support for other version control systems like mercurial. This should be
  easy, it's just a matter of implementing the functions defined in
  gitlint/git.py.
* Support windows.

Changelog
=========

v0.0.5 (2014-05-09)
-------------------

* Added linters: ruby-lint, rubocop, checkstyle, pmd
* Variables %(REPO_HOME)s and %(DEFAULT_CONFIGS)s can be specified in configuration
* Added default pylintrc configuration

v0.0.4 (2014-05-08)
-------------------

* Added linters: html, tidy, scss
* Added way to override default configuration
* Improvements for Python3

v0.0.3 (2014-02-02)
-------------------

* Fixes to the filter syntax
* Fixes to the git parser
* Added linters (YAML, Ini, PHP) and improved linter for PNG and JPEG.
* Improved pylint configuration.
* Improved phpcs configuration.
* Check if program is available and if not display info to install it.
* Cache the output of linters, so subsequent calls are much faster.

v0.0.2 (2013-10-20)
-------------------

* Fixes to the installer

v0.0.1 (2013-10-20)
-------------------

* Initial commit with the basic functionalities. Released mainly to collect
  feedback about the features and the planned ideas.
