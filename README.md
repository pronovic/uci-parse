# UCI Parse Library

![](https://img.shields.io/pypi/l/uciparse.svg)
![](https://img.shields.io/pypi/wheel/uciparse.svg)
![](https://img.shields.io/pypi/pyversions/uciparse.svg)
![](https://github.com/pronovic/uciparse/workflows/Test%20Suite/badge.svg)
![](https://readthedocs.org/projects/uciparse/badge/?version=latest&style=flat)

This is a Python 3 library that understands how to parse and emit 
OpenWRT [uci](https://oldwiki.archive.openwrt.org/doc/uci) configuration files.

It was written to ease OpenWRT upgrades, making it easier to see the
differences between two config files.  As of this writing (mid-2020), OpenWRT
upgrades often don't normalize upgraded config files in the same way from
version to version.  For instance, one version might use single quotes on all
lines, while another version might not use quotes at all.  This makes it very
difficult understand the often-minimal differences between an upgraded file and
the original file.

Developer documentation is found in [DEVELOPER.md](DEVELOPER.md).  See that
file for notes about how the code is structured, how to set up a development
environment, etc.
