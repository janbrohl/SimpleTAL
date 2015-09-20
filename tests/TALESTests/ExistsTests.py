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

def simpleFunction ():
	return "Hello World"
	
def nestedFunction ():
	return {'nest': simpleFunction}
	
class ExistsTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('top', 'Hello from the top')
		self.context.addGlobal ('alt', 'Wobble the way')
		self.context.addGlobal ('theMap', {'top': 'Hello', 'onelevel': {'top': 'Bye'}})
		self.context.addGlobal ('funcMap', {'simple': simpleFunction, 'nested': nestedFunction})
		self.context.addGlobal ('topFunc', simpleFunction)
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))

	def testOneVarDoesExist (self):
		self._runTest_ ('<html tal:condition="exists:top">Top</html>'
					   ,'<html>Top</html>'
					   ,'Exists check on single variable failed.'
					   )
					   
	def testOneVarDoesNotExist (self):
		self._runTest_ ('<html tal:condition="exists:nosuchvar">Top</html>'
					   ,''
					   ,'Exists check on single variable that does not exist failed.'
					   )
					   
	def testTwoVarDoesExist (self):
		self._runTest_ ('<html tal:condition="exists:nosuchvar | exists:top">Top</html>'
					   ,'<html>Top</html>'
					   ,'Exists check on two variables failed.'
					   )
					   
	def testTwoVarDoesNotExist (self):
		self._runTest_ ('<html tal:condition="exists:nosuchvar | exists:nosuchvar2">Top</html>'
					   ,''
					   ,'Exists check on two variables that dont exist failed.'
					   )
					   
	def testOneFuncExist (self):
		self._runTest_ ('<html tal:condition="exists:topFunc">Top</html>'
					   ,'<html>Top</html>'
					   ,'Exists check on one function failed.'
					   )
		
	def testTwoFuncExist (self):
		self._runTest_ ('<html tal:condition="exists:nosuchvar | exists:topFunc">Top</html>'
					   ,'<html>Top</html>'
					   ,'Exists check on two function failed.'
					   )					   
					   
	def testNothingExists (self):
		self._runTest_ ("<html tal:condition=exists:nothing'>Top</html>"
					   ,'<html>Top</html>'
					   ,'Nothing should exist!'
					   )					   
		

if __name__ == '__main__':
	unittest.main()

