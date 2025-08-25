# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
# pylint: disable=redefined-outer-name

import os
from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from uciparse.uci import (
    UciCommentLine,
    UciConfigLine,
    UciFile,
    UciListLine,
    UciOptionLine,
    UciPackageLine,
    UciParseError,
    _contains_single,
)

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures/test_uci")


def load(path: str) -> Dict[str, List[str]]:
    data = {}
    for f in os.listdir(path):
        p = os.path.join(path, f)
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as r:
                data[f] = r.readlines()
    return data


@pytest.fixture
def original() -> Dict[str, List[str]]:
    return load(os.path.join(FIXTURE_DIR, "original"))


@pytest.fixture
def normalized() -> Dict[str, List[str]]:
    return load(os.path.join(FIXTURE_DIR, "normalized"))


@pytest.fixture
def invalid() -> Dict[str, List[str]]:
    return load(os.path.join(FIXTURE_DIR, "invalid"))


@pytest.fixture
def real() -> Dict[str, List[str]]:
    return load(os.path.join(FIXTURE_DIR, "real"))


class TestUtil:
    """Unit tests utility functions."""

    def test_contains_single(self):
        assert _contains_single("") is False
        assert _contains_single("a") is False
        assert _contains_single("abcde_9231") is False
        assert _contains_single("'") is True
        assert _contains_single("''") is True
        assert _contains_single("'whatever'") is True


class TestUciPackageLine:
    """Unit tests for UciPackageLine."""

    def test_init(self):
        line = UciPackageLine(name="name")
        assert line.name == "name"
        assert line.comment is None
        line = UciPackageLine(name="name", comment="comment")
        assert line.name == "name"
        assert line.comment == "comment"

    def test_normalized(self):
        assert UciPackageLine(name="name").normalized() == "package name\n"
        assert UciPackageLine(name="name", comment="# comment").normalized() == "package name  # comment\n"


class TestUciConfigLine:
    """Unit tests for UciConfigLine."""

    def test_init(self):
        line = UciConfigLine(section="section")
        assert line.section == "section"
        assert line.name is None
        assert line.comment is None
        line = UciConfigLine(section="section", name="name", comment="comment")
        assert line.section == "section"
        assert line.name == "name"
        assert line.comment == "comment"

    def test_normalized(self):
        assert UciConfigLine(section="section").normalized() == "\nconfig section\n"
        assert UciConfigLine(section="section", name="name").normalized() == "\nconfig section name\n"
        assert UciConfigLine(section="section", comment="# comment").normalized() == "\nconfig section  # comment\n"
        assert (
            UciConfigLine(section="section", name="name", comment="# comment").normalized() == "\nconfig section name  # comment\n"
        )


class TestUciOptionLine:
    """Unit tests for UciOptionLine."""

    def test_init(self):
        line = UciOptionLine(name="name", value="value")
        assert line.name == "name"
        assert line.value == "value"
        assert line.comment is None
        line = UciOptionLine(name="name", value="value", comment="comment")
        assert line.name == "name"
        assert line.value == "value"
        assert line.comment == "comment"

    def test_normalized(self):
        assert UciOptionLine(name="name", value="").normalized() == "    option name ''\n"
        assert UciOptionLine(name="name", value="one").normalized() == "    option name 'one'\n"
        assert UciOptionLine(name="name", value=" one ").normalized() == "    option name ' one '\n"
        assert UciOptionLine(name="name", value="one two").normalized() == "    option name 'one two'\n"
        assert UciOptionLine(name="name", value="single' quoted").normalized() == '    option name "single\' quoted"\n'
        assert UciOptionLine(name="name", value='double" quoted').normalized() == "    option name 'double\" quoted'\n"
        assert UciOptionLine(name="name", value="one", comment="# comment").normalized() == "    option name 'one'  # comment\n"


class TestUciListLine:
    """Unit tests for UciListLine."""

    def test_init(self):
        line = UciListLine(name="name", value="value")
        assert line.name == "name"
        assert line.value == "value"
        assert line.comment is None
        line = UciListLine(name="name", value="value", comment="comment")
        assert line.name == "name"
        assert line.value == "value"
        assert line.comment == "comment"

    def test_normalized(self):
        assert UciListLine(name="name", value="").normalized() == "    list name ''\n"
        assert UciListLine(name="name", value="one").normalized() == "    list name 'one'\n"
        assert UciListLine(name="name", value=" one ").normalized() == "    list name ' one '\n"
        assert UciListLine(name="name", value="one two").normalized() == "    list name 'one two'\n"
        assert UciListLine(name="name", value="single' quoted").normalized() == '    list name "single\' quoted"\n'
        assert UciListLine(name="name", value='double" quoted').normalized() == "    list name 'double\" quoted'\n"
        assert UciListLine(name="name", value="one", comment="# comment").normalized() == "    list name 'one'  # comment\n"


class TestUciCommentLine:
    """Unit tests for UciCommentLine."""

    def test_init(self):
        line = UciCommentLine(comment="comment")
        assert line.comment == "comment"
        assert line.indented is False
        line = UciCommentLine(comment="comment", indented=True)
        assert line.comment == "comment"
        assert line.indented is True

    def test_normalized(self):
        assert UciCommentLine(comment="# comment", indented=False).normalized() == "# comment\n"
        assert UciCommentLine(comment="# comment", indented=True).normalized() == "    # comment\n"


# pylint: disable=too-many-public-methods
class TestUciFile:
    """Unit tests for UciFile."""

    def test_init(self):
        lines = [MagicMock()]
        ucifile = UciFile(lines=lines)
        assert ucifile.lines == lines

    def test_normalized(self):
        line1 = MagicMock()
        line1.normalized.return_value = "line1\n"
        line2 = MagicMock()
        line2.normalized.return_value = "\nline2\n"
        lines = [line1, line2]
        ucifile = UciFile(lines=lines)
        assert ucifile.normalized() == ["line1\n", "\n", "line2\n"]  # embedded newlines are split out

    def test_from_line(self, normalized):
        path = os.path.join(FIXTURE_DIR, "original", "single-quote")
        ucifile = UciFile.from_file(path=path)
        assert "".join(ucifile.normalized()) == "".join(normalized["single-quote"])

    def test_no_quotes(self, original, normalized):
        ucifile = UciFile.from_lines(original["no-quote"])
        assert "".join(ucifile.normalized()) == "".join(normalized["no-quote"])

    def test_single_quotes(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["single-quote"])
        assert "".join(ucifile.normalized()) == "".join(normalized["single-quote"])

    def test_double_quotes(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["double-quote"])
        assert "".join(ucifile.normalized()) == "".join(normalized["double-quote"])

    def test_no_config_name(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["no-config-name"])
        assert "".join(ucifile.normalized()) == "".join(normalized["no-config-name"])

    def test_comments(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["comments"])
        assert "".join(ucifile.normalized()) == "".join(normalized["comments"])

    def test_package_only(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["package-only"])
        assert "".join(ucifile.normalized()) == "".join(normalized["package-only"])

    def test_config_only(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["config-only"])
        assert "".join(ucifile.normalized()) == "".join(normalized["config-only"])

    def test_option_only(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["option-only"])
        assert "".join(ucifile.normalized()) == "".join(normalized["option-only"])

    def test_list_only(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["list-only"])
        assert "".join(ucifile.normalized()) == "".join(normalized["list-only"])

    def test_option_empty_value(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["option-empty-value"])
        assert "".join(ucifile.normalized()) == "".join(normalized["option-empty-value"])

    def test_list_empty_value(self, original, normalized):
        ucifile = UciFile.from_lines(lines=original["list-empty-value"])
        assert "".join(ucifile.normalized()) == "".join(normalized["list-empty-value"])

    def test_unknown_line(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: unrecognized line type"):
            UciFile.from_lines(lines=invalid["unknown-line"])

    def test_invalid_package_empty(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid package line"):
            UciFile.from_lines(lines=invalid["package-empty"])

    def test_invalid_config_empty(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid config line"):
            UciFile.from_lines(lines=invalid["config-empty"])

    def test_invalid_option_empty(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid option line"):
            UciFile.from_lines(lines=invalid["option-empty"])

    def test_invalid_list_empty(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid list line"):
            UciFile.from_lines(lines=invalid["list-empty"])

    def test_invalid_package_quotes(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid package line"):
            UciFile.from_lines(lines=invalid["package-quotes"])

    def test_invalid_config_quotes(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid config line"):
            UciFile.from_lines(lines=invalid["config-quotes1"])
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid config line"):
            UciFile.from_lines(lines=invalid["config-quotes2"])

    def test_invalid_option_quotes(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid option line"):
            UciFile.from_lines(lines=invalid["option-quotes1"])
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid option line"):
            UciFile.from_lines(lines=invalid["option-quotes2"])

    def test_invalid_list_quotes(self, invalid):
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid list line"):
            UciFile.from_lines(lines=invalid["list-quotes1"])
        with pytest.raises(UciParseError, match=r"Error on line 1: invalid list line"):
            UciFile.from_lines(lines=invalid["list-quotes2"])

    def test_real(self, real):
        for filename in [filename for filename in real if filename != "README.md"]:
            # just check that these real-ish files can be read and normalized successfully
            ucifile = UciFile.from_lines(lines=real[filename])
            ucifile.normalized()
