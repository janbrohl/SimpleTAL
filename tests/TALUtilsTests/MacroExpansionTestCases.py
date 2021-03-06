#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#    Copyright (c) 2016, Jan Brohl <janbrohl@t-online.de>
#    All rights reserved.
#    See LICENSE.txt

#    Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
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
"""		
		
		Unit test cases.
		
"""

from __future__ import unicode_literals
import unittest
import os
import codecs
import io
import logging
import logging.config

from simpletal import simpleTALUtils, simpleTALES, simpleTAL

macroTemplate = simpleTAL.compileHTMLTemplate("""<html>
<body metal:define-macro="one">World is <i metal:define-slot="blue">White</i></body>
</html>
""")

# print "Macro is: %s" % str (macroTemplate)


class MacroExpansionTestCases(unittest.TestCase):
    def setUp(self):
        self.context = simpleTALES.Context()
        entry = """Some structure: <b tal:content="weblog/subject"></b>"""

        weblog = {'subject': 'Test subject', 'entry': entry}

        self.context.addGlobal('test', 'testing')
        self.context.addGlobal('mac', macroTemplate)
        self.context.addGlobal('two', ["one", "two"])
        self.context.addGlobal('three', [1, "Two", 3])
        self.context.addGlobal('weblog', weblog)

    def _runTest_(self, template, txt, result, errMsg="Error"):
        f = io.StringIO()
        simpleTALUtils.expandMacros(self.context, template, f)
        realResult = f.getvalue()
        self.assertEqual(
            realResult, result,
            "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s"
            % (errMsg, txt, realResult, result, template))

    def testMacroExpansionSlots(self):
        txt = '<html><div metal:use-macro="mac/macros/one">Hello<b metal:fill-slot="blue">Blue</b></div></html>'
        template = simpleTAL.compileHTMLTemplate(txt)
        self._runTest_(
            template, txt,
            '<html><body metal:use-macro="mac/macros/one">World is <b metal:fill-slot="blue">Blue</b></body></html>',
            'Expasion with slots failed.')

    def testXMLMacroExpansionSlots(self):
        txt = '<?xml version="1.0" encoding="utf-8"?>\n<html><div metal:use-macro="mac/macros/one">Hello<b metal:fill-slot="blue">Blue</b></div></html>'
        template = simpleTAL.compileXMLTemplate(txt)
        self._runTest_(
            template, txt,
            '<?xml version="1.0"?>\n<html><body metal:use-macro="mac/macros/one">World is <b metal:fill-slot="blue">Blue</b></body></html>',
            'Expansion with slots failed.')


if __name__ == '__main__':
    unittest.main()
