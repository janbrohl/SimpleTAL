# -*- coding: iso-8859-1 -*-

#    Copyright (c) 2016, Jan Brohl <janbrohl@t-online.de>
#    All rights reserved.
#    See LICENSE.txt

#    Copyright (c) 2005 Colin Stewart (http://www.owlfish.com/)
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions
#    are met:
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. The name of the author may not be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
#    IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#    OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#    IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
#    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#    NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
#    THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#    If you make any bug fixes or feature enhancements please let me know!

from __future__ import unicode_literals
from __future__ import absolute_import

METAL_NAME_URI = "http://xml.zope.org/namespaces/metal"
"METAL namespace URI"

TAL_NAME_URI = "http://xml.zope.org/namespaces/tal"
"TAL namespace URI"

# All commands are of the form (opcode, args, commandList)
# The numbers are the opcodes, and also the order of priority

TAL_DEFINE = 1
"Argument: [(isLocalFlag (Y/n), variableName, variablePath),...]"

TAL_CONDITION = 2
"Argument: expression, endTagSymbol"

TAL_REPEAT = 3
"Argument: (varname, expression, endTagSymbol)"

TAL_CONTENT = 4
"Argument: (replaceFlag, type, expression)"

TAL_REPLACE = 5
"Not used in byte code, only ordering."

TAL_ATTRIBUTES = 6
"Argument: [(attributeName, expression)]"

TAL_OMITTAG = 7
"Argument: expression"

TAL_START_SCOPE = 8
"Argument: (originalAttributeList, currentAttributeList)"

TAL_OUTPUT = 9
"Argument: String to output"

TAL_STARTTAG = 10
"Argument: None"

TAL_ENDTAG_ENDSCOPE = 11
"Argument: Tag, omitTagFlag"

TAL_NOOP = 13
"Argument: None"

# METAL Starts here
METAL_USE_MACRO = 14
"Argument: expression, slotParams, endTagSymbol"

METAL_DEFINE_SLOT = 15
"Argument: macroName, endTagSymbol"

METAL_FILL_SLOT = 16
"Only used for parsing"

METAL_DEFINE_MACRO = 17
"Only used for parsing"

HTML4_VOID_ELEMENTS = frozenset([
    'AREA', 'BASE', 'BASEFONT', 'BR', 'COL', 'FRAME', 'HR', 'IMG', 'INPUT',
    'ISINDEX', 'LINK', 'META', 'PARAM'
])
"""
The set of elements in HTML4 that can not have end tags

Source: http://www.w3.org/TR/html401/index/elements.html
"""

HTML5_VOID_ELEMENTS = frozenset([
    'AREA', 'BASE', 'BR', 'COL', 'COMMAND', 'EMBED', 'HR', 'IMG', 'INPUT',
    'KEYGEN', 'LINK', 'META', 'PARAM', 'SOURCE', 'TRACK', 'WBR'
])
"""
The set of elements in HTML5 that can not have end tags

Source: http://www.w3.org/TR/html-markup/syntax.html#void-element
"""

HTML_FORBIDDEN_ENDTAG = HTML4_VOID_ELEMENTS | HTML5_VOID_ELEMENTS
"""
The set of elements in HTML5 that can not have end tags
"""

HTML_BOOLEAN_ATTS = frozenset(
    [('AREA', 'NOHREF'), ('IMG', 'ISMAP'), ('OBJECT', 'DECLARE'), ('INPUT',
                                                                   'CHECKED'),
     ('INPUT', 'DISABLED'), ('INPUT', 'READONLY'), ('INPUT', 'ISMAP'),
     ('SELECT', 'MULTIPLE'), ('SELECT', 'DISABLED'), ('OPTGROUP', 'DISABLED'),
     ('OPTION', 'SELECTED'), ('OPTION', 'DISABLED'), ('TEXTAREA', 'DISABLED'),
     ('TEXTAREA', 'READONLY'), ('BUTTON', 'DISABLED'), ('SCRIPT', 'DEFER')])
"""
Set of element:attribute pairs that can use minimized form in HTML
"""


class SignalValue(object):
    """ Helper class to make unique values with a useful __str__"""

    def __init__(self, info):
        self.__info = info

    def __str__(self):
        return self.__info


DEFAULTVALUE = SignalValue("This constant represents a default value.")
