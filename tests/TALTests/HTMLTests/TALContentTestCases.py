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
	
class TALContentTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		entry = """Some structure: <b tal:content="weblog/subject"></b>"""
		
		weblog = {'subject': 'Test subject', 'entry': entry}
		
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		self.context.addGlobal ('weblog', weblog)
		
	def _runTest_ (self, txt, result, errMsg="Error", allowTALInStructure=1):
		file = StringIO.StringIO (txt)
		realResult = simpleTAL.expandTemplate (file, self.context, allowTALInStructure=allowTALInStructure)
		self.failUnless (realResult == result, "%s - passed in: %s got back %s expected %s" % (errMsg, txt, realResult, result))
						
	def testContentNothing (self):
		self._runTest_ ('<html><p tal:content="nothing"></p></html>'
						,'<html><p></p></html>'
						,'Content of nothing did not evaluate to empty tag.')
						
	def testContentDefault (self):
		self._runTest_ ('<html><p tal:content="default">Original</p></html>'
						,'<html><p>Original</p></html>'
						,'Content of default did not evaluate to existing content')
	
	def testContentString (self):
		self._runTest_ ('<html><p tal:content="test">Original</p></html>'
						,'<html><p>testing</p></html>'
						,'Content of string did not evaluate to contain string')
						
	def testContentStructure (self):
		self._runTest_ ('<html><p tal:content="structure weblog/entry">Original</p></html>'
						,'<html><p>Some structure: <b>Test subject</b></p></html>'
						,'Content of Structure did not evaluate to expected result')   
						
	def testTALDisabledContentStructure (self):
		self._runTest_ ('<html><p tal:content="structure weblog/entry">Original</p></html>'
						,'<html><p>Some structure: <b tal:content="weblog/subject"></b></p></html>'
						,'Content of Structure did not evaluate to expected result'
						,allowTALInStructure=0)  
						
if __name__ == '__main__':
	unittest.main()
	
