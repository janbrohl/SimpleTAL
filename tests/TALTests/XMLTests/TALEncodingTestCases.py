#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""		Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
		All rights reserved.
		
		Redistribution and use in source and binary forms, with or without
		modification, are permitted provided that the following conditions
		are met:
		1. Redistributions of source code must retain the above copyright
		   notice, this list of conditions and the following disclaimer.
		2. Redistributions in binary form must reproduce the above copyright
		   notice, this list of conditions and the following disclaimer in the
		   documentation and/or other materials provided with the distribution.
		3. The name of the author may not be used to endorse or promote products
		   derived from this software without specific prior written permission.
		
		THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
		IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
		OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
		IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
		INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
		NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
		DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
		THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
		THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""

import unittest, os
import StringIO, codecs
import logging, logging.config

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
isoDecoder = codecs.lookup ("iso-8859-1")[1]
	
class TALEncodingTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'Testing this and that')
		self.context.addGlobal ('HighBC', isoDecoder ('This cost nothing, yep £0!')[0])
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testISOToUTF8 (self):
		utf8Pound = "\xc2\xa3"
		template = simpleTAL.compileXMLTemplate ('<?xml version="1.0" encoding="iso-8859-1"?>\n<html>£3.12?  <b tal:replace="HighBC"></b></html>')
		file = StringIO.StringIO()
		template.expand (self.context, file, 'utf-8')
		result = file.getvalue()
		expectedResult = '<?xml version="1.0"?>\n<html>' + utf8Pound + "3.12?  This cost nothing, yep " + utf8Pound + "0!</html>"
		self.failUnless (result == expectedResult, "UTF8 Encoding failed.  \nResult was: " + result + "\nExpected result: " + expectedResult)
		
	def testISOToISO (self):
		template = simpleTAL.compileXMLTemplate ('<?xml version="1.0" encoding="iso-8859-1"?>\n<html>£3.12?  <b tal:replace="HighBC"></b></html>')
		file = StringIO.StringIO()
		template.expand (self.context, file, 'iso-8859-1')
		result = file.getvalue()
		expectedResult = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>£3.12?  This cost nothing, yep £0!</html>'
		self.failUnless (result == expectedResult, "ISO Encoding failed.  \nResult was: " + result + "\nExpected result: " + expectedResult)
	
	def testUTF8ToISO (self):
		template = simpleTAL.compileXMLTemplate ('<?xml version="1.0"?>\n<html>\xc2\xa33.12?  <b tal:replace="HighBC"></b></html>')
		file = StringIO.StringIO()
		template.expand (self.context, file, 'iso-8859-1')
		result = file.getvalue()
		expectedResult = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>£3.12?  This cost nothing, yep £0!</html>'
		self.failUnless (result == expectedResult, "UTF8 -> ISO Encoding failed.  \nResult was: " + result + "\nExpected result: " + expectedResult)
		
if __name__ == '__main__':
	unittest.main()

