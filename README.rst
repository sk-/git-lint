Git-Lint
========

.. image:: https://badge.fury.io/py/git-lint.svg
    :target: http://badge.fury.io/py/git-lint

.. image:: https://travis-ci.org/sk-/git-lint.svg?branch=master
    :target: https://travis-ci.org/sk-/git-lint

.. image:: https://coveralls.io/repos/sk-/git-lint/badge.svg?branch=master
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

  * `yamllint <https://github.com/adrienverge/yamllint>`_

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
  * `Checkstyle <http://checkstyle.sourceforge.net/>`_

- Coffeescript

  * `coffeelint <http://www.coffeelint.org/>`_

- C++

  * `cpplint <https://github.com/google/styleguide/tree/gh-pages/cpplint>`_

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

* {REPO_HOME}: the root of your repo.
* {DEFAULT_CONFIGS}: the location of the default config files.

If you need to include strings like `{}` or `{foo}` in your command, you need to
double the braces as in `{{}}` or `{{foo}}`.

Git Configuration
-----------------

git-lint comes with a pre-commit hook for git. To install it for your repo
execute::

  $ ln -s `which pre-commit.git-lint.sh` $PATH_TO_YOUR_REPO/.git/hooks/pre-commit

or if you want to install it globally execute instead::

  $ ln -s `which pre-commit.git-lint.sh` /usr/share/git-core/templates/hooks/pre-commit


Mercurial Configuration
-----------------------

To make available git-lint with a better name in mercurial you have to add the following
to your .hgrc configuration::

  [alias]
  lint = !git-lint $@

To add a pre-commit hook add the following::

  [hooks]
  pretxncommit.hglint = pre-commit.hg-lint.sh > `tty`


The hook above has a hack to display the output of the command. Additionally,
as mercurial does not provide (AFAIK) any way to skip a hook, if you want to force a commit
with linter warnings execute the commit command as follow::

  $ NO_VERIFY=1 hg commit ...

Note though that mercurial heavily uses commit to leverage all of their commands/extensions.
I've found that setting any sort of precommit hook will get on your way when using common
actions as ``rebase`` or ``shelve``.

Limitations
-----------

In some cases a change will trigger a warning in another line. Those cases are
unfortunately not handled by git-lint, as it only reports those lines that were
modified. Fully supporting this use case would require running the linters twice
and reporting only the new lines. The most common case in which this occurs is with
unused imports or variables. Let's say we have the following piece of code::

  import foo
  foo.bar()

If you remove the second line, git-lint will not complain as the warning is for line
1, which was not modified.

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
* Add support for more version control systems (svn, perforce). This should be
  easy, it's just a matter of implementing the functions defined in
  gitlint/git.py or gitlint/hg.py.
* Support windows.

Contributors
============

* `Rovanion Luckey <https://github.com/Rovanion>`_
* `Radek Simko <https://github.com/radeksimko>`_
* `Adrien Vergé <https://github.com/adrienverge>`_
* `Rob Rodrigues <https://github.com/irialad>`_


Changelog
=========

v0.0.9 (2018-01-22)
-------------------

* Fixed versioning to match in both pip install and package
* Added multithreading support

v0.0.8 (2015-10-14)
-------------------

* Fixed git pre commit hook (thanks to Rovanion Luckey)
* Fixed issues #64, #67

v0.0.7 (2015-06-28)
-------------------

* Better support in python 3
* Removed support for Python 3.2
* Output is sorted by line and column number
* Bugfixes: issues #49, #50, #54, #62
* Added coffelint support
* Improved defaults

v0.0.6 (2014-09-08)
-------------------

* Added mercurial support
* Run e2e tests on Travis

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
