# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:

from unittest.mock import MagicMock, call, patch

import pytest

from uciparse.cli import diff, parse
from uciparse.uci import UciParseError


class TestUciParse:
    """
    Unit tests for the uciparse script.
    """

    def test_h(self):
        with patch("sys.argv", ["uciparse", "-h"]):
            with pytest.raises(SystemExit):
                parse()

    def test_help(self):
        with patch("sys.argv", ["uciparse", "--help"]):
            with pytest.raises(SystemExit):
                parse()

    def test_no_file(self):
        with patch("sys.argv", ["uciparse"]):
            with pytest.raises(SystemExit):
                parse()

    @patch("uciparse.cli.sys.stdin")
    @patch("uciparse.cli.sys.stdout.writelines")
    @patch("uciparse.cli.UciFile")
    def test_stdin(self, ucifile, writelines, stdin):
        with patch("sys.argv", ["uciparse", "-"]):
            uci = MagicMock()
            uci.normalized.return_value = ["normalized"]
            ucifile.from_fp.return_value = uci
            parse()
            ucifile.from_fp.assert_called_once_with(stdin)
            writelines.assert_called_once_with(["normalized"])

    @patch("uciparse.cli.sys.stdout.writelines")
    @patch("uciparse.cli.UciFile")
    def test_file(self, ucifile, writelines):
        with patch("sys.argv", ["uciparse", "file"]):
            uci = MagicMock()
            uci.normalized.return_value = ["normalized"]
            ucifile.from_file.return_value = uci
            parse()
            ucifile.from_file.assert_called_once_with("file")
            writelines.assert_called_once_with(["normalized"])

    @patch("uciparse.cli.sys.stderr.write")
    @patch("uciparse.cli.UciFile")
    def test_error(self, ucifile, write):
        with patch("sys.argv", ["uciparse", "file"]):
            exception = UciParseError(message="Hello")
            ucifile.from_file.side_effect = exception
            with pytest.raises(SystemExit):
                parse()
            ucifile.from_file.assert_called_once_with("file")
            write.assert_called_once_with("Hello\n")


class TestUciDiff:
    """
    Unit tests for the ucidiff script.
    """

    def test_h(self):
        with patch("sys.argv", ["ucidiff", "-h"]):
            with pytest.raises(SystemExit):
                diff()

    def test_help(self):
        with patch("sys.argv", ["ucidiff", "--help"]):
            with pytest.raises(SystemExit):
                diff()

    def test_no_file(self):
        with patch("sys.argv", ["ucidiff"]):
            with pytest.raises(SystemExit):
                diff()

    def test_one_file(self):
        with patch("sys.argv", ["ucidiff"]):
            with pytest.raises(SystemExit):
                diff()

    @patch("uciparse.cli.difflib.unified_diff")
    @patch("uciparse.cli.sys.stdout.writelines")
    @patch("uciparse.cli.UciFile")
    def test_file(self, ucifile, writelines, unified_diff):
        with patch("sys.argv", ["ucidiff", "a", "b"]):
            left = MagicMock()
            left.normalized.return_value = ["left"]
            right = MagicMock()
            right.normalized.return_value = ["right"]
            ucifile.from_file.side_effect = [left, right]
            unified_diff.return_value = ["diff"]
            diff()
            ucifile.from_file.assert_has_calls([call("a"), call("b")])
            writelines.assert_called_once_with(["diff"])
            unified_diff.assert_called_once_with(a=["left"], b=["right"], fromfile="a", tofile="b")

    @patch("uciparse.cli.sys.stderr.write")
    @patch("uciparse.cli.UciFile")
    def test_error(self, ucifile, write):
        with patch("sys.argv", ["ucidiff", "a", "b"]):
            exception = UciParseError(message="Hello")
            ucifile.from_file.side_effect = exception
            with pytest.raises(SystemExit):
                diff()
            ucifile.from_file.assert_called_once_with("a")
            write.assert_called_once_with("Hello\n")
