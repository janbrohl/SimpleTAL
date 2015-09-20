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
	
class TALHandlerTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testEmptyFile (self):
		self._runTest_ ("", "", "Empty template contains more text than given.")
						
	def testSingleEmptyElement (self):
		self._runTest_ ("<single>", "<single>")
						
	def testSingleElement (self):
		self._runTest_ ("<single>start</single>", "<single>start</single>")
		
	def testUnbalancedDocument (self):
		self._runTest_ ("<single>start<b>end</b>", "<single>start<b>end</b>")
		
	def testNoCloseElement (self):
		self._runTest_ ("<p>Hello.<br>World</p>", "<p>Hello.<br>World</p>")

	def testCaseSensitivity (self):
		self._runTest_ ("<p>Hello.<br><b>World</B></p>", "<p>Hello.<br><b>World</b></p>")
		
	def testComments (self):
		self._runTest_ ("<html><!-- This is a comment <here> --><p>Boo</p></html>", "<html><!-- This is a comment <here> --><p>Boo</p></html>")
				
	def testUnbalancedCloseTag (self):
		try:
			template = simpleTAL.compileHTMLTemplate ("<p>Hello</b> World</p>")
			file = StringIO.StringIO ()
			template.expand (self.context, file)
			realResult = file.getvalue()
			self.fail ("No exception raised during parsing of unbalanced tag.")
		except simpleTAL.TemplateParseException, e:
			pass
    
	def testEncodedCharsSection (self):
		self._runTest_ ("""<p>&lt;section&gt; stuff &amp; things.</p>"""
									 ,"""<p>&lt;section&gt; stuff &amp; things.</p>"""
									 ,"Quoted chars were not re-encoded correctly.")
									 
	def testDocumentTypeDeclaration (self):
		self._runTest_("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"><html><p tal:content="test"></p></html>"""
									,"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN"><html><p>testing</p></html>"""
									,"""Document type was not output correctly."""
									)
									
	def testHTMLComments (self):
		self._runTest_("""<html><!-- Tal content coming up.--><p tal:content="test"></p></html>"""
									,"""<html><!-- Tal content coming up.--><p>testing</p></html>"""
									,"""Comment not output correctly."""
									)
		

if __name__ == '__main__':
	unittest.main()
	
