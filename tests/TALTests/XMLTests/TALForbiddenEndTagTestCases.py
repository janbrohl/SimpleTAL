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
	
class TALForbiddenEndTagTestCases (unittest.TestCase):
	""" Tests to prove that XML templates do not perform end tag suppression on HTML elements
			that have forbidden end tags in HTML 4.01.  See equivalent HTML test cases for end
			tag suppression.
	"""
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('link', 'www.owlfish.com')
		self.context.addGlobal ('scrWidth', '640')
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileXMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testAreaElement (self):
		self._runTest_ ('<html><area tal:attributes="href link"></area></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><area href="www.owlfish.com"></area></html>'
										,"HTML Element AREA did NOT produce end tag.")

	def testBaseElement (self):
		self._runTest_ ('<html><base tal:attributes="href link"></base></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><base href="www.owlfish.com"></base></html>'
										,"HTML Element BASE did NOT produce end tag.")

	def testBaseFontElement (self):
		self._runTest_ ('<html><basefont tal:attributes="font test"></basefont></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><basefont font="testing"></basefont></html>'
										,"HTML Element BASEFONT did NOT produce end tag.")
										
	def testBRElement (self):
		self._runTest_ ('<html><br tal:attributes="class test"></br></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><br class="testing"></br></html>'
										,"HTML Element BR did NOT produce end tag.")

	def testColElement (self):
		self._runTest_ ('<html><col tal:attributes="width scrWidth"></col></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><col width="640"></col></html>'
										,"HTML Element COL did NOT produce end tag.")

	def testFrameElement (self):
		self._runTest_ ('<html><frame tal:attributes="href link"></frame></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><frame href="www.owlfish.com"></frame></html>'
										,"HTML Element FRAME did NOT produce end tag.")
										
	def testHRElement (self):
		self._runTest_ ('<html><hr tal:attributes="class test"></hr></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><hr class="testing"></hr></html>'
										,"HTML Element HR did NOT produce end tag.")
										
	def testImgElement (self):
		self._runTest_ ('<html><img tal:attributes="src link"></img></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><img src="www.owlfish.com"></img></html>'
										,"HTML Element IMG did NOT produce end tag.")
										
	def testInputElement (self):
		self._runTest_ ('<html><input tal:attributes="name test"></input></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><input name="testing"></input></html>'
										,"HTML Element INPUT did NOT produce end tag.")
										
	def testIsIndexElement (self):
		self._runTest_ ('<html><isindex tal:attributes="name test"></isindex></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><isindex name="testing"></isindex></html>'
										,"HTML Element ISINDEX did NOT produce end tag.")

	def testLinkElement (self):
		self._runTest_ ('<html><link tal:attributes="href link"></link></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><link href="www.owlfish.com"></link></html>'
										,"HTML Element LINK did NOT produce end tag.")

	def testMetaElement (self):
		self._runTest_ ('<html><meta tal:attributes="name test"></meta></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><meta name="testing"></meta></html>'
										,"HTML Element META did NOT produce end tag.")

	def testParamElement (self):
		self._runTest_ ('<html><param tal:attributes="name test"></param></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><param name="testing"></param></html>'
										,"HTML Element PARAM did NOT produce end tag.")
										
if __name__ == '__main__':
	unittest.main()

