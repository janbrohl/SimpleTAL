#!/usr/bin/python
""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""

import unittest, os
import StringIO
import logging, logging.config

import simpleTAL, simpleTALES

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
	
