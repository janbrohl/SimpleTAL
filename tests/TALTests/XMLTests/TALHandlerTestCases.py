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
from __future__ import print_function

import unittest
import os
import sys
import io
import logging
import logging.config

try:
    # check to see if pyxml is installed
    from xml.sax.saxlib import LexicalHandler
    use_lexical_handler = 1
except ImportError:
    use_lexical_handler = 0

    class LexicalHandler:
        pass


from simpletal import simpleTAL, simpleTALES

import xml.etree.ElementTree as ET
import xmlcompare

if (os.path.exists("logging.ini")):
    logging.config.fileConfig("logging.ini")
else:
    logging.basicConfig()


class TALHandlerTestCases(unittest.TestCase):
    def setUp(self):
        self.context = simpleTALES.Context()
        self.context.addGlobal('test', 'testing')
        self.context.addGlobal('one', [1])
        self.context.addGlobal('two', ["one", "two"])
        self.context.addGlobal('three', [1, "Two", 3])

    def _runTest_(self, txt, result, errMsg="Error"):
        template = simpleTAL.compileXMLTemplate(txt)
        file = io.StringIO()
        template.expand(self.context, file, outputEncoding="iso-8859-1")
        realResult = file.getvalue()
        try:
            expectedElement = ET.fromstring(result)
        except Exception as e:
            self.fail("Exception (%s) thrown parsing XML expected result: %s" %
                      (str(e), result))

        try:
            realElement = ET.fromstring(realResult)
        except Exception as e:
            self.fail(
                "Exception (%s) thrown parsing XML actual result: %s\nPage Template: %s"
                % (str(e), realResult, str(template)))

        self.assertTrue(
            xmlcompare.equal(expectedElement, realElement),
            "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s"
            % (errMsg, txt, realResult, result, template))

    def testSingleEmptyElement(self):
        self._runTest_(
            "<single/>",
            '<?xml version="1.0" encoding="iso-8859-1"?>\n<single/>')

    def testSingleElement(self):
        self._runTest_(
            "<single>start</single>",
            '<?xml version="1.0" encoding="iso-8859-1"?>\n<single>start</single>'
        )

    def testSingleElementSpaces(self):
        self._runTest_(
            '<html><br/><br /><br  	/></html>',
            '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><br/><br/><br/></html>'
        )

    def testSingleElementNewLines(self):
        self._runTest_(
            '<html><br\n/><br /><br  \n	/></html>',
            '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><br/><br/><br/></html>'
        )

    def testSingleElementEasyAttributes(self):
        self._runTest_(
            '<html><br class="test"/></html>',
            '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><br class="test"/></html>'
        )

    def testSingleElementHardAttributes(self):
        self._runTest_(
            """<html><br this="this" /><br other="that" that="this"/><br test="/>difficult" bad="Hard />"/></html>""",
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><br this="this"/><br other="that" that="this"/><br test="/>difficult" bad="Hard />"/></html>"""
        )

    def testSingleElementHarderAttributes(self):
        self._runTest_(
            """<html xmlns:gold="http://gold" gold:define-macro="m1" ><br gold:define-slot="sl1"/></html>""",
            """<html xmlns:gold="http://gold" gold:define-macro="m1"><br gold:define-slot="sl1"/></html>"""
        )

    def testCDATASection(self):
        self._runTest_(
            "<single><![CDATA[Here's some <escaped> CDATA section stuff & things.]]></single>",
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<single>Here's some &lt;escaped&gt; CDATA section stuff &amp; things.</single>""",
            "CDATA section was not re-encoded correctly.")

    def testNameSpaces(self):
        self._runTest_(
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<test1:html xmlns:test2="http://test2" xmlns:test1="http://test1"><test2:p>Testing</test2:p></test1:html>""",
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<test1:html xmlns:test2="http://test2" xmlns:test1="http://test1"><test2:p>Testing</test2:p></test1:html>""",
            """Namespaces not preserved.""")

    def testProcessingInstructions(self):
        self._runTest_(
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<p>Some<?test testInstruction="yes" doNothing="yes"?><i>markup</i></p>""",
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<p>Some<?test testInstruction="yes" doNothing="yes"?><i>markup</i></p>""",
            """Processing instructions not preserved.""")

    def testCommentHandling(self):
        if (not use_lexical_handler):
            return

        self._runTest_(
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<p><!-- This is a <b>test -->Here</p>""",
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<p><!-- This is a <b>test -->Here</p>""",
            "Comments not preserved.")

    def testDocumentTypeDeclaration(self):
        txt = """<?xml version="1.0" encoding="iso-8859-1"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html><p>Test</p></html>"""
        template = simpleTAL.compileXMLTemplate(txt)
        fh = io.StringIO()
        template.expand(
            self.context,
            fh,
            docType=
            """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3c.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""",
            outputEncoding="iso-8859-1")
        realResult = fh.getvalue()
        expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3c.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html><p>Test</p></html>"""
        self.assertEqual(
            realResult, expectedResult,
            "Doctype failed - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s"
            % (txt, realResult, expectedResult, str(template)))

    def testXMLDeclarationSuppressionWithDocType(self):
        txt = """<?xml version="1.0" encoding="iso-8859-1"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html><p>Test</p></html>"""
        template = simpleTAL.compileXMLTemplate(txt)
        fh = io.StringIO()
        template.expand(
            self.context,
            fh,
            docType=
            """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3c.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""",
            suppressXMLDeclaration=1)
        realResult = fh.getvalue()
        expectedResult = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3c.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html><p>Test</p></html>"""
        self.assertEqual(
            realResult, expectedResult,
            "Doctype failed - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s"
            % (txt, realResult, expectedResult, str(template)))

    def testNBSPparsing(self):
        txt = """<?xml version="1.0" encoding="iso-8859-1"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html><p>Test&nbsp;Space</p></html>"""
        template = simpleTAL.compileXMLTemplate(txt)
        fh = io.StringIO()
        if use_lexical_handler:
            template.expand(self.context, fh)
        else:
            template.expand(
                self.context,
                fh,
                docType=
                """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">"""
            )
        realResult = fh.getvalue()
        expectedResult = b"""<?xml version="1.0"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html><p>Test\xa0Space</p></html>""".decode(
            "iso-8859-1")
        self.assertEqual(
            realResult, expectedResult,
            "NBSP expansion failed - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s"
            % (txt, realResult, expectedResult, template))

    def testXMLDeclarationSuppressionWithNoDocType(self):
        txt = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><p>Test</p></html>"""
        template = simpleTAL.compileXMLTemplate(txt)
        fh = io.StringIO()
        template.expand(self.context, fh, suppressXMLDeclaration=1)
        realResult = fh.getvalue()
        expectedResult = """<html><p>Test</p></html>"""
        self.assertEqual(
            realResult, expectedResult,
            "Doctype failed - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s"
            % (txt, realResult, expectedResult, str(template)))

    def testDTDPassthru(self):
        if not use_lexical_handler:
            return
        self._runTest_(
            """<?xml version="1.0" encoding="iso-8859-1"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"><html><head><title>Hi</title></head><body></body></html>""",
            """<?xml version="1.0" encoding="iso-8859-1"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n<html><head><title>Hi</title></head><body></body></html>"""
        )

    def testSampleXHTML11Doc(self):
        """
        Cut and pasted right out of the xhtml 1.1 spec
        """

        if not use_lexical_handler:
            return
        self._runTest_("""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >
  <head>
    <title>Virtual Library</title>
  </head>
  <body>
    <p>Moved to <a href="http://vlib.org/">vlib.org</a>.</p>
  </body>
</html>
""", """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >
  <head>
    <title>Virtual Library</title>
  </head>
  <body>
    <p>Moved to <a href="http://vlib.org/">vlib.org</a>.</p>
  </body>
</html>
""")


if __name__ == '__main__':
    unittest.main()
