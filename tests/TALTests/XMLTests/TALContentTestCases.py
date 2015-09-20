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

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
class TALContentTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		entry = """<insertedData>Some structure: <b tal:content="weblog/subject"></b></insertedData>"""
		
		weblog = {'subject': 'Test subject', 'entry': entry}
		
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		self.context.addGlobal ('weblog', weblog)
		
	def _runTest_ (self, txt, result, errMsg="Error", allowTALInStructure=1):
		template = simpleTAL.compileXMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testContentNothing (self):
		self._runTest_ ('<html><p tal:content="nothing"></p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><p></p></html>'
						,'Content of nothing did not evaluate to empty tag.')
						
	def testContentDefault (self):
		self._runTest_ ('<html><p tal:content="default">Original</p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><p>Original</p></html>'
						,'Content of default did not evaluate to existing content')
	
	def testContentString (self):
		self._runTest_ ('<html><p tal:content="test">Original</p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><p>testing</p></html>'
						,'Content of string did not evaluate to contain string')
						
	def testContentStructure (self):
		# This test has specific needs - i.e. wrap the weblog/entry in a template...		
		entry = """<insertedData>Some structure: <b tal:content="weblog/subject"></b></insertedData>"""
		weblog = {'subject': 'Test subject', 'entry': simpleTAL.compileXMLTemplate(entry)}
		self.context.addGlobal ('weblog', weblog)
		
		self._runTest_ ('<html><p tal:content="structure weblog/entry">Original</p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><p><insertedData>Some structure: <b>Test subject</b></insertedData></p></html>'
						,'Content of Structure did not evaluate to expected result')   

	def testTALDisabledContentStructure (self):
		self._runTest_ ('<html><p tal:content="structure weblog/entry">Original</p></html>'
						,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><p><insertedData>Some structure: <b tal:content="weblog/subject"></b></insertedData></p></html>'
						,'Content of Structure did not evaluate to expected result'
						,allowTALInStructure=0)  
						
if __name__ == '__main__':
	unittest.main()
	
