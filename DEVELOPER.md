# Developer Notes

## Supported Platforms

This code should work equivalently on MacOS, Linux, and Windows.

## Packaging and Dependencies

This project uses [Poetry](https://python-poetry.org/) to manage Python packaging and dependencies.  Most day-to-day tasks (such as running unit tests from the command line) are orchestrated through Poetry.

A coding standard is enforced using [Black](https://pypi.org/project/black/), [isort](https://pypi.org/project/isort/) and [Pylint](https://pypi.org/project/pylint/).  Python 3 type hinting is validated using [MyPy](https://pypi.org/project/mypy/).

## Pre-Commit Hooks

We rely on pre-commit hooks to ensure that the code is properly-formatted,
clean, and type-safe when it's checked in.  The `run install` step described
below installs the project pre-commit hooks into your repository.  These hooks
are configured in [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

If necessary, you can temporarily disable a hook using Git's `--no-verify`
switch.  However, keep in mind that the CI build on GitHub enforces these
checks, so the build will fail.

## Line Endings

The [`.gitattributes`](.gitattributes) file controls line endings for the files
in this repository.  Instead of relying on automatic behavior, the
`.gitattributes` file forces most files to have UNIX line endings.

## Prerequisites

Nearly all prerequisites are managed by Poetry.  All you need to do is make
sure that you have a working Python 3 enviroment and install Poetry itself.

### Poetry Version

The project is designed to work with Poetry >= 1.8.0.  If you already have an older
version of Poetry installed on your system, upgrade it first.

### MacOS

On MacOS, it's easiest to use [Homebrew](https://brew.sh/) to install Python and pipx:

```
brew install python3 pipx
```

Once that's done, make sure the `python` on your `$PATH` is Python 3 from
Homebrew (in `/usr/local`), rather than the standard Python 2 that comes with
older versions of MacOS.

Finally, install Poetry itself and then verify your installation:

```
pipx install poetry
pipx inject poetry poetry-dynamic-versioning
pipx list --include-injected
```

To upgrade this installation later, use:

```
pipx upgrade --include-injected poetry
```

### Debian

First, install Python 3 and related tools:

```
sudo apt-get install python3 python-is-python3 pipx
```

Once that's done, make sure that the `python` interpreter on your `$PATH` is
Python 3.

Finally, install Poetry itself and then verify your installation:

```
pipx install poetry
pipx inject poetry poetry-dynamic-versioning
pipx list --include-injected
```

To upgrade this installation later, use:

```
pipx upgrade --include-injected poetry
```

### Windows

First, install Python 3 from your preferred source, either a standard
installer or a meta-installer like Chocolatey.  Make sure the `python`
on your `$PATH` is Python 3.

Next, install pipx:

```
python -m pip install --user pipx
```

Finally, install Poetry itself and then verify your installation:

```
pipx install poetry
pipx inject poetry poetry-dynamic-versioning
pipx list --include-injected
```

To upgrade this installation later, use:

```
pipx upgrade --include-injected poetry
```

> _Note:_ The development environment (the `run` script, etc.) expects a bash
> shell to be available.  On Windows, it works fine with the standard Git Bash.

## Developer Tasks

The [`run`](run) script provides shortcuts for common developer tasks:

```
$ ./run --help

------------------------------------
Shortcuts for common developer tasks
------------------------------------

Basic tasks:

- run install: Setup the virtualenv via Poetry and install pre-commit hooks
- run format: Run the code formatters
- run checks: Run the code checkers
- run build: Build artifacts in the dist/ directory
- run test: Run the unit tests
- run test -c: Run the unit tests with coverage
- run test -ch: Run the unit tests with coverage and open the HTML report
- run suite: Run the complete test suite, as for the GitHub Actions CI build

Additional tasks:

- run docs: Build the Sphinx documentation for readthedocs.io
- run docs -o: Build the Sphinx documentation and open in a browser
- run release: Tag and release the code, triggering GHA to publish artifacts
```

## Integration with PyCharm

Currently, I use [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download) as
my day-to-day IDE.  By integrating Black and Pylint, most everything important
that can be done from a shell environment can also be done right in PyCharm.

PyCharm offers a good developer experience.  However, the underlying configuration
on disk mixes together project policy (i.e. preferences about which test runner to
use) with system-specific settings (such as the name and version of the active Python
interpreter). This makes it impossible to commit complete PyCharm configuration
to the Git repository.  Instead, the repository contains partial configuration, and
there are instructions below about how to manually configure the remaining items.

### Prerequisites

Before going any further, make sure sure that you have installed all of the system
prerequisites discussed above.  Then, make sure your environment is in working
order.  In particular, if you do not run the install step, there will be no
virtualenv for PyCharm to use:

```
./run install && ./run suite
```

### Open the Project

Once you have a working shell development environment, **Open** (do not
**Import**) the `uci-parse` directory in PyCharm, then follow the remaining
instructions below.  By using **Open**, the existing `.idea` directory will be
retained and all of the existing settings will be used.

### Interpreter

As a security precaution, PyCharm does not trust any virtual environment
installed within the repository, such as the Poetry `.venv` directory. In the
status bar on the bottom right, PyCharm will report _No interpreter_.  Click
on this error and select **Add Interpreter**.  In the resulting dialog, click
**Ok** to accept the selected environment, which should be the Poetry virtual
environment.

### Project Structure

Go to the PyCharm settings and find the `uci-parse` project.  Under 
**Project Structure**, mark both `src` and `tests` as source folders.  In 
the **Exclude Files** box, enter the following: 

```
LICENSE;NOTICE;PyPI.md;.coverage;.coveragerc;.github;.gitignore;.gitattributes;.htmlcov;.idea;.isort.cfg;.mypy.ini;.mypy_cache;.pre-commit-config.yaml;.pylintrc;.pytest_cache;.readthedocs.yml;.tabignore;build;dist;docs/_build;out;poetry.lock;poetry.toml;run;.run;.venv;
```

When you're done, click **Ok**.  Then, go to the gear icon in the project panel
and uncheck **Show Excluded Files**.  This will hide the files and directories
in the list above.

### Tool Preferences

In the PyCharm settings, go to **Editor > Inspections** and be sure that the
**Project Default** profile is selected.

Unit tests are written using [Pytest](https://docs.pytest.org/en/latest/),
and API documentation is written
using [Google Style Python Docstring](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).  However,
neither of these is the default in PyCharm.  In the PyCharm settings, go to
**Tools > Python Integrated Tools**.  Under **Testing > Default test runner**,
select _pytest_.  Under **Docstrings > Docstring format**, select _Google_.

### Running Unit Tests

Right click on the `tests` folder in the project explorer and choose **Run
'pytest in tests'**.  Make sure that all of the tests pass.  If you see a slightly
different option (i.e. for "Unittest" instead of "pytest") then you probably
skipped the preferences setup discussed above.  You may need to remove the
run configuration before PyCharm will find the right test suite.

### External Tools

Optionally, you might want to set up external tools for some of common
developer tasks: code reformatting and the PyLint and MyPy checks.  One nice
advantage of doing this is that you can configure an output filter, which makes
the Pylint and MyPy errors clickable.  To set up external tools, go to PyCharm
settings and find **Tools > External Tools**.  Add the tools as described
below.

#### Linux or MacOS

On Linux or MacOS, you can set up the external tools to invoke the `run` script
directly.

##### Shell Environment

For this to work, it's important that tools like `poetry` are on the system
path used by PyCharm.  On Linux, depending on how you start PyCharm, your
normal shell environment may or may not be inherited.  For instance, I had to
adjust the target of my LXDE desktop shortcut to be the script below, which
sources my profile before running the `pycharm.sh` shell script:

```sh
#!/bin/bash
source ~/.bash_profile
/opt/local/lib/pycharm/pycharm-community-2020.3.2/bin/pycharm.sh
```

##### Format Code

|Field|Value|
|-----|-----|
|Name|`Format Code`|
|Description|`Run the code formatters`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`format`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Checked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Unchecked_|
|Make console active on message in stderr|_Unchecked_|
|Output filters|_Empty_|

##### Run MyPy Checks

|Field|Value|
|-----|-----|
|Name|`Run MyPy Checks`|
|Description|`Run the MyPy code checks`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`mypy`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Unchecked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Checked_|
|Make console active on message in stderr|_Checked_|
|Output filters|`$FILE_PATH$:$LINE$:$COLUMN$:.*`|

##### Run Pylint Checks

|Field|Value|
|-----|-----|
|Name|`Run Pylint Checks`|
|Description|`Run the Pylint code checks`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`pylint`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Unchecked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Checked_|
|Make console active on message in stderr|_Checked_|
|Output filters|`$FILE_PATH$:$LINE$:$COLUMN.*`|

#### Windows

On Windows, PyCharm has problems invoking the `run` script.  The trick is to
invoke the Bash interpreter and tell it to invoke the `run` script.  The
examples below assume that you have installed Git Bash in its standard location
under `C:\Program Files\Git`.  If it is somewhere else on your system, just
change the path for `bash.exe`.

##### Format Code

|Field|Value|
|-----|-----|
|Name|`Format Code`|
|Description|`Run the code formatters`|
|Group|`Developer Tools`|
|Program|`powershell.exe`|
|Arguments|`& 'C:\Program Files\Git\bin\bash.exe' -l "./run" format | Out-String`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Checked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Unchecked_|
|Make console active on message in stderr|_Unchecked_|
|Output filters|_Empty_|

##### Run MyPy Checks

|Field|Value|
|-----|-----|
|Name|`Run MyPy Checks`|
|Description|`Run the MyPy code checks`|
|Group|`Developer Tools`|
|Program|`powershell.exe`|
|Arguments|`& 'C:\Program Files\Git\bin\bash.exe' -l "./run" mypy | Out-String`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Unchecked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Checked_|
|Make console active on message in stderr|_Checked_|
|Output filters|`$FILE_PATH$:$LINE$:$COLUMN$:.*`|

##### Run Pylint Checks

|Field|Value|
|-----|-----|
|Name|`Run Pylint Checks`|
|Description|`Run the Pylint code checks`|
|Group|`Developer Tools`|
|Program|`powershell.exe`|
|Arguments|`& 'C:\Program Files\Git\bin\bash.exe' -l "./run" pylint | Out-String`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Unchecked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Checked_|
|Make console active on message in stderr|_Checked_|
|Output filters|`$FILE_PATH$:$LINE$:$COLUMN.*`|

## Release Process

### Documentation

Documentation at [Read the Docs](https://uci-parse.readthedocs.io/en/stable/)
is generated via a GitHub hook.  So, there is no formal release process for the
documentation.

### Code

Code is released to [PyPI](https://pypi.org/project/uciparse/).  There is a
partially-automated process to publish a new release.

> _Note:_ In order to publish code, you must must have push permissions to the
> GitHub repo.

Ensure that you are on the `master` branch.  Releases must always be done from
`master`.

Ensure that the `Changelog` is up-to-date and reflects all of the changes that
will be published.  The top line must show your version as unreleased:

```
Version 0.1.29     unreleased
```

Run the release command:

```
./run release 0.1.29
```

This command updates `NOTICE` and `Changelog` to reflect the release version
and release date, commits those changes, tags the code, and pushes to GitHub.
The new tag triggers a GitHub Actions build that runs the test suite, generates
the artifacts, publishes to PyPI, and finally creates a release from the tag.

> _Note:_ This process relies on a PyPI API token with upload permissions for
> the project.  This token is stored in a GitHub Actions secret called
> `PYPI_TOKEN`.
