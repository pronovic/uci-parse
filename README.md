# UCI Parse Library

[![pypi](https://img.shields.io/pypi/v/uciparse.svg)](https://pypi.org/project/uciparse/)
[![license](https://img.shields.io/pypi/l/uciparse.svg)](https://github.com/pronovic/uci-parse/blob/master/LICENSE)
[![wheel](https://img.shields.io/pypi/wheel/uciparse.svg)](https://pypi.org/project/uciparse/)
[![python](https://img.shields.io/pypi/pyversions/uciparse.svg)](https://pypi.org/project/uciparse/)
[![Test Suite](https://github.com/pronovic/uci-parse/workflows/Test%20Suite/badge.svg)](https://github.com/pronovic/uci-parse/actions?query=workflow%3A%22Test+Suite%22)
[![docs](https://readthedocs.org/projects/uci-parse/badge/?version=stable&style=flat)](https://uci-parse.readthedocs.io/en/stable/)
[![coverage](https://coveralls.io/repos/github/pronovic/uci-parse/badge.svg?branch=master)](https://coveralls.io/github/pronovic/uci-parse?branch=master)

Python 3 library and command line tools to parse, diff, and normalize OpenWRT
[UCI](https://openwrt.org/docs/guide-user/base-system/uci) configuration files.

These tools were written to ease OpenWRT upgrades, making it easier to see the
differences between two config files.  As of this writing (mid-2020), OpenWRT
upgrades often don't normalize upgraded config files in the same way from
version to version.  For instance, the new version from `opkg upgrade` (saved
off with a `-opkg` filename) might use single quotes on all lines, while the
original version on disk might not use quotes at all.  This makes it very
difficult understand the often-minimal differences between an upgraded file and
the original file.

## Developer Doumentation

Developer documentation is found in [DEVELOPER.md](DEVELOPER.md).  See that
file for notes about how the code is structured, how to set up a development
environment, etc.

## Installing the Package

Installing this package on your OpenWRT router is not as simple as it could be.
A lot of routers do not have enough space available to install a full version
of Python including `pip` or `setuptools`.  If yours does have lots of space,
it's as simple as this:

```
$ opkg update
$ opkg install python3-pip
$ pip3 install uciparse
```

If not, it gets a little ugly.  First, install `wget` with support for HTTPS:

```
$ opkg update
$ opkg install wget libustream-openssl20150806 ca-bundle ca-certificates
```

Then, go to [PyPI](https://pypi.org/project/uciparse/#files) and copy the
URL for the source package `.tar.gz` file.  Retrieve the source package 
with `wget` and then manually extract it:

```
$ wget https://files.pythonhosted.org/.../uciparse-0.1.8.tar.gz
$ tar zxvf uciparse-0.1.8.tar.gz
$ cd uciparse-0.1.8
```

Finally, run the custom install script provided with the source package:

```
$ sh ./scripts/install
```

This installs the OpenWRT `python3-light` package, then copies the Python
packages into the right `site-packages` directory and the `uciparse` and
`ucidiff` scripts to `/usr/bin`.

## Using the Tools

Once you have installed the package as described above, the `uciparse` and
`ucidiff` tools will be available in your path.  

### ucidiff

The `ucidiff` tool is probably the tool you'll use most often when updating
your router.  It reads two UCI configuration files from disk, normalizes both in
memory (without making changes on disk), and then compares them.  The result is
a unified diff, like `diff -Naur`.  This gives you a way to understand the real
differences between two files without ever having to change anything on disk.

```
$ ucidiff --help
usage: ucidiff [-h] a b

Diff two UCI configuration files.

positional arguments:
  a           Path to the first UCI file to compare
  b           Path to the second UCI file to compare

optional arguments:
  -h, --help  show this help message and exit

The comparison is equivalent to a 'diff -Naur' between the normalized versions
of the files. If either file can't be parsed, then an error will be returned
and no diff will be shown.
```

### uciparse

If you would prefer to clean up and normalize your configuration files on disk,
then you can use the `uciparse` tool.  It reads a UCI config file from disk or
from `stdin`, parses it, and prints normalized output to `stdout`.  

```
$ uciparse --help
usage: uciparse [-h] uci

Parse and normalize a UCI configuration file.

positional arguments:
  uci         Path to the UCI file to normalize, or '-' for stdin

optional arguments:
  -h, --help  show this help message and exit

Results will be printed to stdout. If the file can't be parsed then an error
will be returned and no output will be generated.
```

Before using ``uciparse``, you should make a backup of any config file that you
are going to normalize.
