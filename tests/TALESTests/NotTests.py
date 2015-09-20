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

def simpleFunction ():
	return "Hello"
	
def simpleFalseFunc ():
	return 0
			
class NotTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('top', 'Hello from the top')
		self.context.addGlobal ('alt', 'Wobble the way')
		self.context.addGlobal ('holder', {'helloFunc': simpleFunction
										  ,'falseFunc': simpleFalseFunc})		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))

	def testNotNothing (self):
		self._runTest_ ('<html tal:condition="not:nothing">Exists</html>'
					   ,'<html>Exists</html>'
					   ,'not:nothing returned false'
					   )
					   
	def testNotDefault (self):
		self._runTest_ ('<html tal:condition="not:default">Exists</html>'
					   ,''
					   ,'not:default returned true'
					   )

	def testNotNoSuchPath (self):
		self._runTest_ ('<html tal:condition="not:no/such/path">Exists</html>'
					   ,'<html>Exists</html>'
					   ,'not:no/such/path returned false'
					   )

	def testNotSomething (self):
		self._runTest_ ('<html tal:condition="not:holder/helloFunc">Exists</html>'
					   ,''
					   ,'not:string returned true'
					   )

	def testNotFalse (self):
		self._runTest_ ('<html tal:condition="not:holder/falseFunc">Exists</html>'
					   ,'<html>Exists</html>'
					   ,'not:false returned false'
					   )

	def testNotExists (self):
		self._runTest_ ('<html tal:condition="not:exists:nothing">Exists</html>'
					   ,''
					   ,'not:exists:nothing returned true'
					   )
					   
	def testNotORPathOne (self):
		self._runTest_ ('<html tal:condition="not:no/such/path | holder/helloFunc">Exists</html>'
					   ,''
					   ,'not:no/such/path | holder/helloFunc returned true'
					   )
					   
	def testNotORPathTwo (self):
		self._runTest_ ('<html tal:condition="not:no/such/path | holder/falseFunc">Exists</html>'
					   ,'<html>Exists</html>'
					   ,'not:no/such/path | holder/falseFunc returned false'
					   )
					   
	def testNotORPathThree (self):
		self._runTest_ ('<html tal:condition="no/such/path | not:holder/helloFunc">Exists</html>'
					   ,''
					   ,'no/such/path | not:holder/helloFunc returned true'
					   )

	def testNotORPathFour (self):
		self._runTest_ ('<html tal:condition="no/such/path | not:holder/falseFunc">Exists</html>'
					   ,'<html>Exists</html>'
					   ,'no/such/path | not:holder/falseFunc returned false'
					   )
					   					   	
if __name__ == '__main__':
	unittest.main()

