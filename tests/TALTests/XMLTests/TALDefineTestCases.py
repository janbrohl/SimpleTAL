#!/usr/bin/python
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
import StringIO
import logging, logging.config

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
class TALDefineTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileXMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testDefineString (self):
		self._runTest_ ('<html tal:define="def1 test"><p tal:content="def1"></p></html>', '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><p>testing</p></html>', "Simple string define failed.")
		
	def testDefineList (self):
		self._runTest_ ('<html tal:define="def1 two"><p tal:repeat="var def1">Hello <b tal:content="var"></b></p></html>'
						, '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><p>Hello <b>one</b></p><p>Hello <b>two</b></p></html>', 'List define failed.')
						
	def testDefineGlobal (self):
		self._runTest_ ('<html><p tal:define="global def1 test"></p><p tal:content="def1"></p></html>'
						, '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><p></p><p>testing</p></html>', 'Global did not set globally')

	def testDefineLocal (self):
		self._runTest_ ('<html><p tal:define="local def1 test"></p><p tal:content="def1"></p></html>'
						, '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><p></p><p></p></html>', 'Explicit local available globaly')
						
	def testDefineImplicitLocal (self):
		self._runTest_ ('<html><p tal:define="def1 test"></p><p tal:content="def1"></p></html>'
						, '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><p></p><p></p></html>', 'Implicit local available globaly')

	def testDefineMultipleLocal (self):
		self._runTest_ ('<html><div tal:define="firstVar test;secondVar string:This is a semi;;colon;thirdVar string:Test"><p tal:content="test">Testing</p><p tal:content="secondVar"></p><p tal:content="thirdVar"></p></div></html>'
						, '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><div><p>testing</p><p>This is a semi;colon</p><p>Test</p></div></html>', 'Multiple defines failed.')
		
	def testDefineMultipleMixed (self):
		self._runTest_ ('<html><div tal:define="firstVar test;global secondVar string:This is a semi;;colon;thirdVar string:Test"><p tal:content="test">Testing</p><p tal:content="secondVar"></p><p tal:content="thirdVar"></p></div><b tal:content="secondVar"></b></html>'
						, '<?xml version="1.0" encoding="iso-8859-1"?>\n<html><div><p>testing</p><p>This is a semi;colon</p><p>Test</p></div><b>This is a semi;colon</b></html>', 'Multiple defines failed.')

if __name__ == '__main__':
	unittest.main()

