# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:

r"""
Implements code to parse and emit the OpenWRT UCI_ configuration format.

Normalizing a File
==================

When normalizing a file, the goal is to standardize indenting, comment
placement, and quoting, without changing the semantics of the file. We do this
by reading in the file per the spec, and then emitting the same configuration
in a standard way.  

We always emit identifiers unquoted.  We always emit values quoted, using a single
quote unless the value contains a single quote, in which case we'll use double
quotes.  We always indent 4 spaces.  We always put a blank line before a config
section.  We always put a single space between fields on a single line and two
spaces before a comment.  None of this is configurable.

The one thing we can't handle well is a standalone comment.  Since the file
format is line-oriented, we don't really have any context for comments.  The
best we can do is infer that a comment is supposed to be indented at the same
level as an option or list if there was any whitespace before the leading ``#``
character when we found the comment.


Parser Design
=============

These regular expressions tell us what sort of line we're dealing with:

    - **Empty line:** ``(^\s*$)``
    - **Comment-only line:** ``(^\s*#.*$)``
    - **Package line:** ``(^\s*)(package)(\s+)(.*?)(\s*$)``
    - **Config line:** ``(^\s*)(config)(\s+)(.*?)(\s*$)``
    - **Option line:** ``(^\s*)(option)(\s+)(.*?)(\s*$)``
    - **List line:** ``(^\s*)(list)(\s+)(.*?)(\s*$)``

Any line that does not match one of these regular expressions is an invalid
line per the specification.  

We can simplify these regular expressions into a single check:

   ``(^\s*$)|((^\s*)(#)(.*$))|((^\s*)(package|config|option|list)(\s+)(.*?)(\s*$))``

With this regular expression, if group #4 is `#`, then we have a comment,
with the comment text in group #5 and leading whitespace in group #3.  Otherwise,
group #8 gives us the type of the line (``package``, ``config``, ``option`` 
or ``list``) and group #10 gives us the remainder of the line after the type.

Next, we need to parse the data on each line according to the individual rules
for the type of line.  The UCI restrictions on identifiers are enforced,
including that empty identifiers are not legal.  We also enforce quoting rules,
including that quotes must match.  

The spec is silent about embedded and escaped quotes within option values.
I've chosen to assume that a double-quoted string may contain single quotes and
vice-versa (like in Python or Perl) but that escaped quotes are not allowed.  

We do not validate boolean values.  The spec supports a specific list, but you
can't really identify from looking at the file whether an option is supposed to
be a boolean or just a string. 

Regardless, if the first regular expression matches a line, and the second
regular expression does not, then the line isn't valid and we can't process it.
If we can't process any line, we'll bomb out and refuse to process the file
at all.

For a package line, we can use this regular expression:

``(^)((([\"'])([a-zA-Z0-9_-]+)(?:\4))|([a-zA-Z0-9_-]+))((\s*)(#.*))?($)``

If the field is quoted, this yields the package name in group #5.  If the field
is not quoted, this yields the package name in group #6.  The comment, if it
exists, will be in group #9.

For a config line, we can use this regular expression:

``(^)((([\"'])([a-zA-Z0-9_-]+)(?:\4))|([a-zA-Z0-9_-]+))((\s+)((([\"'])([a-zA-Z0-9_-]+)(?:\11))|([a-zA-Z0-9_-]+)))?((\s*)(#.*))?($)``

If the first field is quoted, this yields the section type in group #5.  If the
first field is not quoted, this yields the section type in group #6.  If the
second field exists and is quoted, this yields the the section name in group
#12.  If second field is not quoted, this yields the section name in group #9.
The trailing comment, if it exists, will be in group #16, with leading
whitespace stripped.

The list and option lines are slightly different, since the value is required
and is not an identifier:

``(^)((([\"'])([a-zA-Z0-9_-]+)(?:\4))|([a-zA-Z0-9_-]+))(\s+)((([\"'])([^\\\10]*)(?:\10))|([^'\"\s#]+))((\s*)(#.*))?($)``

If first field is quoted, this yields the list or option name in group #5.  If
the first field is not quoted, this yields the list or option name in group #6.
If second field is quoted, this yields the value in group #11.  If second field
is not quoted, this yields the value in group #8.  The trailing comment, if it
exists, will be in group #15, with trailing whitespace stripped.  The regular
expression is careful to allow only embedded quotes of a different type, as
discussed above.


UCI Syntax Specification
========================

*Note:* This section was taken from the OpenWRT UCI_ documentation.  

The UCI configuration files usually consist of one or more config statements,
so called sections with one or more option statements defining the actual
values.

A ``#`` begins comments in the usual way. Specifically, if a line contains a
``#`` outside of a string literal, it and all characters after it in the line
are considered a comment and ignored.

Below is an example of a simple configuration file::

    package 'example'
     
    config 'example' 'test'
            option   'string'      'some value'
            option   'boolean'     '1'
            list     'collection'  'first item'
            list     'collection'  'second item'
        
The config ``'example' 'test'`` statement defines the start of a section with
the type ``example`` and the name ``test``. There can also be so called anonymous
sections with only a type, but no name identifier. The type is important for
the processing programs to decide how to treat the enclosed options.

The option ``'string' 'some value'`` and option ``'boolean' '1'`` lines define simple
values within the section. Note that there are no syntactical differences
between text and boolean options. Per convention, boolean options may have one
of the values `0``, ``no``, ``off``, ``false`` or ``disabled`` to specify a false value
or ``1`` , ``yes``, ``on``, ``true`` or ``enabled`` to specify a true value.  In the
lines starting with a `list` keyword an option with multiple values is defined.
All `list` statements that share the same name, `collection` in our example, will
be combined into a single list of values with the same order as in the
configuration file.  The indentation of the `option` and `list` statements is a
convention to improve the readability of the configuration file but it's not
syntactically required.

Usually you do not need to enclose identifiers or values in quotes. Quotes are
only required if the enclosed value contains spaces or tabs. Also it's legal to
use double- instead of single-quotes when typing configuration options.

All of the examples below are valid UCI syntax::

    option  example   value
    option  example  "value"
    option 'example'  value
    option 'example' "value"
    option "example" 'value'

In contrast, the following examples are not valid UCI syntax::

    # missing quotes around the value
    option  example   v_a l u-e
    # unbalanced quotes
    option 'example" "value'

It is important to know that UCI identifiers and config file names may contain
only the characters `a-zA-Z`, `0-9` and `_`. E.g. no hyphens (``-``) are allowed.
Option values may contain any character (as long they are properly quoted).

*(Editorial note: the statement above about identifiers is not accurate.  For
instance, the ``/etc/config/wireless`` file uses configuration that looks like
``config wifi-device 'radio0'``, which clearly doesn't meet the spec.  We
accept identifiers that include a dash, regardless of what the spec says.)*

.. _UCI: https://openwrt.org/docs/guide-user/base-system/uci
"""

from __future__ import annotations  # see: https://stackoverflow.com/a/33533514/2907667

import re
from abc import ABC, abstractmethod
from typing import List, Optional, Sequence, TextIO

# Standard indent of 4 spaces
_INDENT = "    "

# Matches any known type of line
_LINE_REGEX = re.compile(r"(^\s*$)|((^\s*)(#)(.*$))|((^\s*)(package|config|option|list)(\s+)(.*?)(\s*$))")

# Matches the remainder of a package line
_PACKAGE_REGEX = re.compile(r"(^)((([\"'])([a-zA-Z0-9_-]+)(?:\4))|([a-zA-Z0-9_-]+))((\s*)(#.*))?($)")

# Matches the remainder of a config line
# pylint: disable=line-too-long
_CONFIG_REGEX = re.compile(
    r"(^)((([\"'])([a-zA-Z0-9_-]+)(?:\4))|([a-zA-Z0-9_-]+))((\s+)((([\"'])([a-zA-Z0-9_-]+)(?:\11))|([a-zA-Z0-9_-]+)))?((\s*)(#.*))?($)"
)

# Matches the remainder of an option or list line
_OPTION_REGEX = LIST_REGEX = re.compile(
    r"(^)((([\"'])([a-zA-Z0-9_-]+)(?:\4))|([a-zA-Z0-9_-]+))(\s+)((([\"'])([^\\\10]*)(?:\10))|([^'\"\s#]+))((\s*)(#.*))?($)"
)


def _contains_single(string: str) -> bool:
    """Whether a string contains a single quote."""
    match = re.search(r"[']", string)
    return match is not None


def _parse_line(lineno: int, line: str) -> Optional[UciLine]:
    """Parse a line, raising UciParseError if it is not valid."""
    match = _LINE_REGEX.match(line)
    if not match:
        raise UciParseError("Error on line %d: unrecognized line type" % lineno)
    if match[4] == "#":
        return _parse_comment(lineno, match[3], match[5])
    elif match[8]:
        if match[8] == "package":
            return _parse_package(lineno, match[10])
        elif match[8] == "config":
            return _parse_config(lineno, match[10])
        elif match[8] == "option":
            return _parse_option(lineno, match[10])
        elif match[8] == "list":
            return _parse_list(lineno, match[10])
    return None


def _parse_package(lineno: int, remainder: str) -> UciPackageLine:
    """Parse a package line, raising UciParseError if it is not valid."""
    match = _PACKAGE_REGEX.match(remainder)
    if not match:
        raise UciParseError("Error on line %d: invalid package line" % lineno)
    name = match[5] if match[5] else match[6]
    comment = match[9]
    return UciPackageLine(name=name, comment=comment)


def _parse_config(lineno: int, remainder: str) -> UciConfigLine:
    """Parse a config line, raising UciParseError if it is not valid."""
    match = _CONFIG_REGEX.match(remainder)
    if not match:
        raise UciParseError("Error on line %d: invalid config line" % lineno)
    section = match[5] if match[5] else match[6]
    name = match[12] if match[12] else match[9]
    comment = match[16]
    return UciConfigLine(section=section, name=name, comment=comment)


def _parse_option(lineno: int, remainder: str) -> UciOptionLine:
    """Parse an option line, raising UciParseError if it is not valid."""
    match = _OPTION_REGEX.match(remainder)
    if not match:
        raise UciParseError("Error on line %d: invalid option line" % lineno)
    name = match[5] if match[5] else match[6]
    value = match[11] if match[11] else match[8] if match[8] not in ('""', "''") else ""
    comment = match[15]
    return UciOptionLine(name=name, value=value, comment=comment)


def _parse_list(lineno: int, remainder: str) -> UciListLine:
    """Parse a list line, raising UciParseError if it is not valid."""
    match = LIST_REGEX.match(remainder)
    if not match:
        raise UciParseError("Error on line %d: invalid list line" % lineno)
    name = match[5] if match[5] else match[6]
    value = match[11] if match[11] else match[8] if match[8] not in ('""', "''") else ""
    comment = match[15]
    return UciListLine(name=name, value=value, comment=comment)


def _parse_comment(_lineno: int, prefix: str, remainder: str) -> UciCommentLine:
    """Parse a comment-only line, raising UciParseError if it is not valid."""
    indented = len(prefix) > 0 if prefix else False  # all we care about is whether it's indented, not the actual indent
    comment = "#%s" % remainder
    return UciCommentLine(comment=comment, indented=indented)


def _serialize_identifier(prefix: str, identifier: Optional[str]) -> str:
    """Serialize an identifier, which is never quoted."""
    return "%s%s" % (prefix, identifier) if identifier else ""


def _serialize_value(prefix: str, value: str) -> str:
    """Serialize an identifier, which is quoted if it contains whitespace or a quote character."""
    quote = "'" if not _contains_single(value) else '"'
    return "%s%s%s%s" % (prefix, quote, value, quote)


def _serialize_comment(prefix: str, comment: Optional[str]) -> str:
    """Serialize a comment, with an optional prefix."""
    return "%s%s" % (prefix, comment) if comment else ""


class UciParseError(ValueError):
    """Exception raised when a UCI file can't be parsed."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UciLine(ABC):
    """A line in a UCI config file."""

    @abstractmethod
    def normalized(self) -> str:
        """Serialize the line in normalized form."""


class UciPackageLine(UciLine):
    """A package line in a UCI config file."""

    def __init__(self, name: str, comment: Optional[str] = None) -> None:
        self.name = name
        self.comment = comment

    def normalized(self) -> str:
        """Serialize the line in normalized form."""
        name_field = _serialize_identifier("package ", self.name)
        comment_field = _serialize_comment("  ", self.comment)
        return "%s%s\n" % (name_field, comment_field)


class UciConfigLine(UciLine):
    """A config line in a UCI config file."""

    def __init__(self, section: str, name: Optional[str] = None, comment: Optional[str] = None) -> None:
        self.section = section
        self.name = name
        self.comment = comment

    def normalized(self) -> str:
        """Serialize the line in normalized form."""
        section_field = _serialize_identifier("\nconfig ", self.section)
        name_field = _serialize_identifier(" ", self.name)
        comment_field = _serialize_comment("  ", self.comment)
        return "%s%s%s\n" % (section_field, name_field, comment_field)


class UciOptionLine(UciLine):
    """An option line in a UCI config file."""

    def __init__(self, name: str, value: str, comment: Optional[str] = None) -> None:
        self.name = name
        self.value = value
        self.comment = comment

    def normalized(self) -> str:
        """Serialize the line in normalized form."""
        name_field = _serialize_identifier(_INDENT + "option ", self.name)
        value_field = _serialize_value(" ", self.value)
        comment_field = _serialize_comment("  ", self.comment)
        return "%s%s%s\n" % (name_field, value_field, comment_field)


class UciListLine(UciLine):
    """A list line in a UCI config file."""

    def __init__(self, name: str, value: str, comment: Optional[str] = None) -> None:
        self.name = name
        self.value = value
        self.comment = comment

    def normalized(self) -> str:
        """Serialize the line in normalized form."""
        name_field = _serialize_identifier(_INDENT + "list ", self.name)
        value_field = _serialize_value(" ", self.value)
        comment_field = _serialize_comment("  ", self.comment)
        return "%s%s%s\n" % (name_field, value_field, comment_field)


class UciCommentLine(UciLine):
    """A comment line in a UCI config file."""

    def __init__(self, comment: str, indented: bool = False) -> None:
        self.comment = comment
        self.indented = indented

    def normalized(self) -> str:
        """Serialize the line in normalized form."""
        indent = _INDENT if self.indented else ""
        comment_field = _serialize_comment(indent, self.comment)
        return "%s\n" % comment_field


class UciFile:
    def __init__(self, lines: List[UciLine]) -> None:
        self.lines = lines

    def normalized(self) -> List[str]:
        """Return a list of normalized lines comprising the file."""
        # We join the lines first and then re-split so we don't end up with lines that have an embedded newline
        return "".join([line.normalized() for line in self.lines]).splitlines(keepends=True)

    # pylint: disable=invalid-name
    @staticmethod
    def from_file(path: str) -> UciFile:
        """Generate a UciFile from a file on disk."""
        with open(path, "r") as fp:
            return UciFile.from_fp(fp)

    @staticmethod
    def from_fp(fp: TextIO) -> UciFile:
        """Generate a UciFile from the contents of a file pointer."""
        return UciFile.from_lines(fp.readlines())

    @staticmethod
    def from_lines(lines: Sequence[str]) -> UciFile:
        """Generate a UciFile from a list of lines."""
        lineno = 0
        ucilines: List[UciLine] = []
        for line in lines:
            lineno += 1
            parsed = _parse_line(lineno, line)
            if parsed:
                ucilines.append(parsed)
        return UciFile(lines=ucilines)
