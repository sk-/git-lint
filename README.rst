Git-Lint
========

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
    * `Pngcrush <http://manpages.ubuntu.com/manpages/raring/man1/pngcrush.1.html>`_

- RST
    * Via `rst2html.py (docutils) <http://docs.python.org/2/library/json.html>`_

- JSON
    * Via python `json.tool module <http://docs.python.org/2/library/json.html>`_

Example use
-----------

::
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

Installation
------------

You can install, upgrade, uninstall pep8.py with these commands::

  $ pip install gitlint
  $ pip install --upgrade gitlint
  $ pip uninstall gitlint

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

* Normalize output. That is try to show a more uniform output, by removing the
  filename and strings like 'line' or 'col'.
* When multiple linters are available sort the output of the linters by line
* Support directories as arguments
* Provide a way to install as a precommit hook
* Provide a man page so 'git help lint' and 'git lint --help' work
* Allow to run a command or function when setting up the linter? These can be
  achieved now by running a bash script wrapping the linter. The rationale for
  this is that some linters, like jshint, only allow iptions to be in a
  configuration file.
* Decide what linter to use based on the whole filename or even in the filetype,
  as returned by the command file.
* Save the last output (raw) for a file and if the modification time is lower
  then do not run the linters and just output what we saved before.
* Provide better options for colorizing the output, and maybe a way to disable
  it. Also detect if colors are supported or if it tty.
* Add a message explaining how to install the executable in case it was not
  found.
* Add support for other version control systems like mercurial. This should be
  easy, it's just a matter of implementing the functions defined in
  gitlint/git.py.
* Support windows.

Changelog
=========
v0.0.2 (2013-10-20)
------------------

* Fixes to the installer

v0.0.1 (2013-10-20)
-------------------

* Initial commit with the basic functionalities. Released mainly to collect
  feedback about the features and the planned ideas.
