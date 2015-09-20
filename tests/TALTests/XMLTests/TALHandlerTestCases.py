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
		template = simpleTAL.compileXMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
												
	def testSingleEmptyElement (self):
		self._runTest_ ("<single/>", '<?xml version="1.0" encoding="iso8859-1"?>\n<single></single>')
						
	def testSingleElement (self):
		self._runTest_ ("<single>start</single>", '<?xml version="1.0" encoding="iso8859-1"?>\n<single>start</single>')
		
	def testCDATASection (self):
		self._runTest_ ("<single><![CDATA[Here's some <escaped> CDATA section stuff & things.]]></single>"
									 ,"""<?xml version="1.0" encoding="iso8859-1"?>\n<single>Here's some &lt;escaped&gt; CDATA section stuff &amp; things.</single>"""
									 ,"CDATA section was not re-encoded correctly.")
									 
	def testNameSpaces (self):
		self._runTest_ ("""<?xml version="1.0" encoding="iso8859-1"?>\n<test1:html xmlns:test1="http://test1" xmlns:test2="http://test2"><test2:p>Testing</test2:p></test1:html>"""
										,"""<?xml version="1.0" encoding="iso8859-1"?>\n<test1:html xmlns:test1="http://test1" xmlns:test2="http://test2"><test2:p>Testing</test2:p></test1:html>"""
										,"""Namespaces not preserved.""")
										
	def testProcessingInstructions (self):
		self._runTest_ ("""<?xml version="1.0" encoding="iso8859-1"?>\n<p>Some<?test testInstruction="yes" doNothing="yes"?><i>markup</i></p>"""
										,"""<?xml version="1.0" encoding="iso8859-1"?>\n<p>Some<?test testInstruction="yes" doNothing="yes"?><i>markup</i></p>"""
										,"""Processing instructions not preserved.""")
		

if __name__ == '__main__':
	unittest.main()
	
