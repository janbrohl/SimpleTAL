#!/usr/bin/python
""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commerical and non-commerical use.
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
	
class TALReplaceTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		entry = """<anEntry>Some structure: <b tal:content="weblog/subject"></b></anEntry>"""
		
		weblog = {'subject': 'Test subject', 'entry': entry}
		
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		self.context.addGlobal ('weblog', weblog)
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileXMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testContentNothing (self):
		self._runTest_ ('<html><p tal:replace="nothing"></p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html></html>'
						,'Content of nothing did not remove tag.')
						
	def testContentDefault (self):
		self._runTest_ ('<html><p tal:replace="default">Original</p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><p>Original</p></html>'
						,'Content of default did not evaluate to existing content without tags')
	
	def testContentString (self):
		self._runTest_ ('<html><p tal:replace="test">Original</p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html>testing</html>'
						,'Content of string did not evaluate to contain string')
						
	def testContentStructure (self):
		# This test has specific needs - i.e. wrap the weblog/entry in a template...		
		entry = """<anEntry>Some structure: <b tal:content="weblog/subject"></b></anEntry>"""
		weblog = {'subject': 'Test subject', 'entry': simpleTAL.compileXMLTemplate(entry)}
		self.context.addGlobal ('weblog', weblog)

		self._runTest_ ('<html><p tal:replace="structure weblog/entry">Original</p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><anEntry>Some structure: <b>Test subject</b></anEntry></html>'
						,'Content of Structure did not evaluate to expected result')    

if __name__ == '__main__':
	unittest.main()
	
