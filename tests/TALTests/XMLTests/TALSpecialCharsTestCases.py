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
import sys
import io
import logging
import logging.config

if sys.version_info >= (3, 0):
    unicode = str

from simpletal import simpleTAL, simpleTALES

if (os.path.exists("logging.ini")):
    logging.config.fileConfig("logging.ini")
else:
    logging.basicConfig()


class TALSpecialCharsTestCases(unittest.TestCase):
    def setUp(self):
        self.context = simpleTALES.Context(allowPythonPath=1)
        self.context.addGlobal('test',
                               '< testing > experimenting & twice as useful')
        self.context.addGlobal('one', [1])
        self.context.addGlobal('two', ["one", "two"])
        self.context.addGlobal('three', [1, "Two", 3])

    def _runTest_(self, txt, result, errMsg="Error", allowTALInStructure=1):
        template = simpleTAL.compileXMLTemplate(txt)
        file = io.StringIO()
        template.expand(self.context, file, outputEncoding="iso-8859-1")
        realResult = file.getvalue()
        self.assertEqual(
            realResult, result,
            "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s"
            % (errMsg, txt, realResult, result, template))

    def testLessThanGreaterThanAmpersand(self):
        self._runTest_(
            '<html tal:content="test">Hello</html>',
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<html>&lt; testing &gt; experimenting &amp; twice as useful</html>""",
            "Less than, greater than or amperand were not encoded correctly")

    def testEscapedPythonPaths(self):
        self._runTest_(
            '<html tal:content="python: str (2000 &lt;&lt; 1)">Hello</html>',
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<html>4000</html>""",
            "Python bit shift failed.")

    def testAmpInTemplate(self):
        self._runTest_(
            """<html tal:attributes="test2 string: Boo There ${test}"><body test="&amp;">Hello Bye Bye</body></html>""",
            """<?xml version="1.0" encoding="iso-8859-1"?>
<html test2="Boo There &lt; testing &gt; experimenting &amp; twice as useful"><body test="&amp;">Hello Bye Bye</body></html>""",
            "&amp; in template failed.")


if __name__ == '__main__':
    unittest.main()
