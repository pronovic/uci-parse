# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:

"""
Implementations for command-line (CLI) tools.
"""

import argparse
import difflib
import sys

from .uci import UciFile, UciParseError


def parse() -> None:
    """Run the uciparse command."""

    parser = argparse.ArgumentParser(
        description="Parse and normalize a UCI configuration file.",
        epilog="Results will be printed to stdout. If the file can't be parsed "
        "then an error will be returned and no output will be generated.",
    )

    parser.add_argument("uci", help="Path to the UCI file to normalize, or '-' for stdin")
    args = parser.parse_args(args=sys.argv[1:])

    try:
        uci = UciFile.from_fp(sys.stdin) if args.uci == "-" else UciFile.from_file(args.uci)
        sys.stdout.writelines(uci.normalized())
    except UciParseError as e:
        sys.stderr.write(e.message + "\n")
        raise SystemExit


# pylint: disable=invalid-name
def diff() -> None:
    """Run the ucidiff command."""
    parser = argparse.ArgumentParser(
        description="Diff two UCI configuration files.",
        epilog="The comparison is equivalent to a 'diff -Naur' between the normalized versions of the files.  "
        "If either file can't be parsed, then an error will be returned and no diff will be shown.",
    )

    parser.add_argument("a", help="Path to the first UCI file to compare")
    parser.add_argument("b", help="Path to the second UCI file to compare")
    args = parser.parse_args(args=sys.argv[1:])

    try:
        a = UciFile.from_file(args.a)
        b = UciFile.from_file(args.b)
        result = difflib.unified_diff(a=a.normalized(), b=b.normalized(), fromfile=args.a, tofile=args.b)
        sys.stdout.writelines(result)
    except UciParseError as e:
        sys.stderr.write(e.message + "\n")
        raise SystemExit
