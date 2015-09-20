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
	
class TALDefineTestCases (unittest.TestCase):
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
							
	def testDefineString (self):
		self._runTest_ ('<html tal:define="def1 test"><p tal:content="def1"></p></html>', "<html><p>testing</p></html>", "Simple string define failed.")
		
	def testDefineList (self):
		self._runTest_ ('<html tal:define="def1 two"><p tal:repeat="var def1">Hello <b tal:content="var"></b></p></html>'
						, '<html><p>Hello <b>one</b></p><p>Hello <b>two</b></p></html>', 'List define failed.')
						
	def testDefineGlobal (self):
		self._runTest_ ('<html><p tal:define="global def1 test"></p><p tal:content="def1"></p></html>'
						, '<html><p></p><p>testing</p></html>', 'Global did not set globally')

	def testDefineLocal (self):
		self._runTest_ ('<html><p tal:define="local def1 test"></p><p tal:content="def1"></p></html>'
						, '<html><p></p><p></p></html>', 'Explicit local available globaly')
						
	def testDefineImplicitLocal (self):
		self._runTest_ ('<html><p tal:define="def1 test"></p><p tal:content="def1"></p></html>'
						, '<html><p></p><p></p></html>', 'Implicit local available globaly')
						
	def testDefineDefault (self):
		self._runTest_ ('<html><p tal:define="global test default"></p><p tal:content="test">Can you see me?</p></html>'
						, '<html><p></p><p>Can you see me?</p></html>', 'Default variable did not define proplerly.')

	def testDefineNothing (self):
		self._runTest_ ('<html><p tal:define="global test nothing"></p><p tal:content="test">Can you see me?</p></html>'
						, '<html><p></p><p></p></html>', 'Nothing variable did not define proplerly.')

		
if __name__ == '__main__':
	unittest.main()

