# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:

"""
Implements code to parse and emit the OpenWRT UCI configuration format.

Normalization Design
====================

When normalizing a file, the goal is to standardize indenting, comment
placement, and quoting, without changing the semantics of the file. We do this
by reading in the file per the spec, and then emitting the same configuration 
in a standard way.  We always emit names and values unquoted unless a quote is
required (i.e. if the string contains whitespace).  We always use single quotes
unless the value contains a single quote, in which case we'll use double
quotes.  We always indent 4 spaces.  We always put a blank line after each
section (after a package or config).  We always put a single space between
fields on a single line.  None of this is configurable.


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

   ``(^\s*$)|((^\s*)(package|config|option|list|#)(\s+)(.*?)(\s*$))``

With this regular expression, if the full match is empty, the line is empty.  
Otherwise, group #4 gives us the type of the line (``package``, ``config``, 
``option``, ``list``, or ``#``) and group #6 gives us the remainder of the 
line after the type.  We can ignore blank lines and blank space preceding 
a comment, since we'll regenerate it according to our own formatting rules.

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

   ``(^)((([\"'])([a-z0-9_]+)(?:\4))|([a-z0-9_]+))((\s*)(#.*))?($)``

If the field is quoted, this yields the package name in group #5.  If the field
is not quoted, this yields the package name in group #6.  The comment, if it
exists, will be in group #9.  

For a config line, we can use this regular expression:

   ``(^)((([\"'])([a-z0-9_]+)(?:\4))|([a-z0-9_]+))((\s+)((([\"'])([a-z0-9_]+)(?:\11))|([a-z0-9_]+)))?((\s*)(#.*))?($)``

If the first field is quoted, this yields the section type in group #5.  If the
first field is not quoted, this yields the section type in group #6.  If the
second field exists and is quoted, this yields the the section name in group
#12.  If second field is not quoted, this yields the section name in group #9.
The trailing comment, if it exists, will be in group #16, with leading
whitespace stripped.

The list and option lines are slightly different, since the value is required
and is not an identifier:

   ``(^)((([\"'])([a-z0-9_]+)(?:\4))|([a-z0-9_]+))(\s+)((([\"'])([^\\10]+)(?:\10))|([^'\"\s]+))((\s*)(#.*))?($)``

If first field is quoted, this yields the list or option name in group #5.  If
the first field is not quoted, this yields the list or option name in group #6.
If second field is quoted, this yields the value in group #11.  If second field
is not quoted, this yields the value in group #8.  The trailing comment, if it
exists, will be in group #15, with trailing whitespace stripped.  The regular
expression is careful to allow only embedded quotes of a different type, as
discussed above.


UCI Syntax Specification
========================

*Note:* This section was taken from the OpenWRT_ documentation.  

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
only the characters `a-z`, `0-9` and `_`. E.g. no hyphens (``-``) are allowed.
Option values may contain any character (as long they are properly quoted).

.. _OpenWRT: https://openwrt.org/docs/guide-user/base-system/uci
"""
