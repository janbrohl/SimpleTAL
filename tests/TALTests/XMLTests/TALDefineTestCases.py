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
	
class TALDefineTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		file = StringIO.StringIO (txt)
		realResult = simpleTAL.expandXMLTemplate (file, self.context)
		self.failUnless (realResult == result, "%s - passed in: %s got back %s expected %s" % (errMsg, txt, realResult, result))
						
	def testDefineString (self):
		self._runTest_ ('<html tal:define="def1 test"><p tal:content="def1"></p></html>', '<?xml version="1.0" encoding="iso8859-1"?>\n<html><p>testing</p></html>', "Simple string define failed.")
		
	def testDefineList (self):
		self._runTest_ ('<html tal:define="def1 two"><p tal:repeat="var def1">Hello <b tal:content="var"></b></p></html>'
						, '<?xml version="1.0" encoding="iso8859-1"?>\n<html><p>Hello <b>one</b></p><p>Hello <b>two</b></p></html>', 'List define failed.')
						
	def testDefineGlobal (self):
		self._runTest_ ('<html><p tal:define="global def1 test"></p><p tal:content="def1"></p></html>'
						, '<?xml version="1.0" encoding="iso8859-1"?>\n<html><p></p><p>testing</p></html>', 'Global did not set globally')

	def testDefineLocal (self):
		self._runTest_ ('<html><p tal:define="local def1 test"></p><p tal:content="def1"></p></html>'
						, '<?xml version="1.0" encoding="iso8859-1"?>\n<html><p></p><p></p></html>', 'Explicit local available globaly')
						
	def testDefineImplicitLocal (self):
		self._runTest_ ('<html><p tal:define="def1 test"></p><p tal:content="def1"></p></html>'
						, '<?xml version="1.0" encoding="iso8859-1"?>\n<html><p></p><p></p></html>', 'Implicit local available globaly')

		
if __name__ == '__main__':
	unittest.main()

