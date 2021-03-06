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
import io
import logging
import logging.config

from simpletal import simpleTAL, simpleTALES

import xml.etree.ElementTree as ET
import xmlcompare

if (os.path.exists("logging.ini")):
    logging.config.fileConfig("logging.ini")
else:
    logging.basicConfig()


class TALSingletonTests(unittest.TestCase):
    def setUp(self):
        self.context = simpleTALES.Context()
        self.context.addGlobal('test', 'testing')
        self.context.addGlobal('one', [1])
        self.context.addGlobal('two', ["one", "two"])
        self.context.addGlobal('three', ['1', "Two", '3'])

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

    def _runMacroTest_(self, macros, page, result, errMsg="Error"):
        macroTemplate = simpleTAL.compileXMLTemplate(macros)
        pageTemplate = simpleTAL.compileXMLTemplate(page)
        self.context.addGlobal("site", macroTemplate)
        self.context.addGlobal("here", pageTemplate)
        file = io.StringIO()
        pageTemplate.expand(self.context, file)
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
                "Exception (%s) thrown parsing XML actual result: %s\nPage Template: %s\nMacro Template: %s"
                % (str(e), realResult, str(pageTemplate), str(macroTemplate)))

        self.assertTrue(
            xmlcompare.equal(expectedElement, realElement),
            "%s - \npassed in macro: %s \n and page: %s\ngot back %s \nexpected %s\n\nPage Template: %s"
            % (errMsg, macros, page, realResult, result, pageTemplate))

    def testDefineAttributes(self):
        self._runTest_(
            """<html><br tal:define="temp test" tal:attributes="href temp"/><br tal:attributes="href temp"/></html>""",
            """<html><br href="testing" /><br/></html>""",
            """Local define followed by attributes and global test failed.""")

    def testConditionDefine(self):
        self._runTest_(
            """<html><br tal:define="global temp test" tal:attributes="href temp"/><br tal:condition="exists: temp"/><img tal:condition="not:exists:temp"/></html>""",
            """<html><br href="testing" /><br/></html>""",
            """Global define and condition failed""")

    def testRepeatAttributes(self):
        self._runTest_(
            """<html><br tal:repeat="temp three" tal:attributes="href temp"/></html>""",
            """<html><br href="1" /><br href="Two"/><br href="3"/></html>""",
            """Repeat and attributes failed.""")

    def testContentRepeat(self):
        self._runTest_(
            """<html><br tal:repeat="temp three" tal:content="temp"/></html>""",
            """<html><br>1</br><br>Two</br><br>3</br></html>""",
            """Content with Repeat failed.""")

    def testReplaceRepeat(self):
        self._runTest_(
            """<html><br tal:repeat="temp three" tal:replace="temp"/></html>""",
            """<html>1Two3</html>""", """Replace with Repeat failed.""")

    def testReplaceRepeatAttributes(self):
        self._runTest_(
            """<html><br tal:repeat="temp three" tal:attributes="href temp" tal:replace="temp"/></html>""",
            """<html>1Two3</html>""", """Replace with Repeat failed.""")

    def testContentRepeatAttributes(self):
        self._runTest_(
            """<html><br tal:repeat="temp three" tal:attributes="href temp" tal:content="temp"/></html>""",
            """<html><br href="1">1</br><br href="Two">Two</br><br href="3">3</br></html>""",
            """Content with Repeat and Attributes failed.""")

    def testOmitTagContentRepeatAttributes(self):
        self._runTest_(
            """<html><br tal:repeat="temp three" tal:omit-tag="default" tal:attributes="href temp" tal:content="temp"/></html>""",
            """<html>1Two3</html>""",
            """OmitTag with Content and Repeat and Attributes failed.""")

    def testDefineMacroSlots(self):
        self._runMacroTest_(
            """<html metal:define-macro="m1"><br metal:define-slot="sl1"/></html>""",
            """<div metal:use-macro="site/macros/m1"><p metal:fill-slot="sl1">Hello</p></div>""",
            """<html><p>Hello</p></html>""",
            """METAL with define-slot on singleton failed.""")

    def testDefineMacro(self):
        self._runMacroTest_(
            """<html metal:define-macro="m1" id="test"/>""",
            """<div metal:use-macro="site/macros/m1"><p metal:fill-slot="sl1">Hello</p></div>""",
            """<html id="test"/>""",
            """METAL with define-macro on singleton failed.""")

    def testUseMacro(self):
        self._runMacroTest_(
            """<html metal:define-macro="m1"><br metal:define-slot="sl1"/></html>""",
            """<div metal:use-macro="site/macros/m1"/>""",
            """<html><br/></html>""",
            """METAL with use-macro on singleton failed.""")

    def testFillSlot(self):
        self._runMacroTest_(
            """<html metal:define-macro="m1"><br metal:define-slot="sl1"/></html>""",
            """<div metal:use-macro="site/macros/m1"><i metal:fill-slot="sl1" id="test"/></div>""",
            """<html><i id="test"/></html>""",
            """METAL with fill-slot on singleton failed.""")

    def testRepeatUseMacro(self):
        self._runMacroTest_(
            """<html metal:define-macro="m1"><br metal:define-slot="sl1"/></html>""",
            """<test><p tal:repeat="nums three"><div metal:use-macro="site/macros/m1"/></p></test>""",
            """<test><p><html><br/></html></p><p><html><br/></html></p><p><html><br/></html></p></test>""",
            """METAL with repeat and use-macro on singleton failed.""")


if __name__ == '__main__':
    unittest.main()
