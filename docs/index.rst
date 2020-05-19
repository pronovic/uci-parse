UCI Parse Library
=================

Release v\ |version|

.. image:: https://img.shields.io/pypi/l/uciparse.svg
    :target: https://pypi.org/project/uciparse/

.. image:: https://img.shields.io/pypi/wheel/uciparse.svg
    :target: https://pypi.org/project/uciparse/

.. image:: https://img.shields.io/pypi/pyversions/uciparse.svg
    :target: https://pypi.org/project/uciparse/

.. image:: https://github.com/pronovic/uci-parse/workflows/Test%20Suite/badge.svg
    :target: https://github.com/pronovic/uci-parse

.. image:: https://readthedocs.org/projects/uci-parse/badge/?version=latest&style=flat
    :target: https://uci-parse.readthedocs.io/en/latest/

This is a Python 3 library that understands how to parse and emit
OpenWRT UCI_ configuration files.


Installation
------------

Install the package with pip::

    $ pip install uciparse


Documentation
-------------

.. toctree::
   :maxdepth: 2
   :glob:


Background and Usage
--------------------

It was written to ease OpenWRT upgrades, making it easier to see the
differences between two config files.  As of this writing (mid-2020), OpenWRT
upgrades often don't normalize upgraded config files in the same way from
version to version.  For instance, the new version from ``opkg upgrade`` (saved
off with a ``.opkg`` extension) might use single quotes on all lines, while the
original version on disk might not use quotes at all.  This makes it very
difficult understand the often-minimal differences between an upgraded file and
the original file.

.. _UCI: https://openwrt.org/docs/guide-user/base-system/uci
