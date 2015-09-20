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

def simpleFunction (param):
	return "Hello %s" % param
	
def exceptionalFunction (param):
	raise Exception (param)
				
class PythonPathTests (unittest.TestCase):
	def setUp (self):
		pass
			
	def _runTest_ (self, txt, result, errMsg="Error", allowPythonPath=0):
		self.context = simpleTALES.Context(allowPythonPath=allowPythonPath)
		self.context.addGlobal ('top', 'Hello from the top')
		self.context.addGlobal ('exceptFunc', exceptionalFunction)		
		self.context.addGlobal ('helloFunc', simpleFunction)
		self.context.addGlobal ('myList', [1,2,3,4,5,6])
		
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))

	def testPythonPathException (self):
		self._runTest_ ("""<html tal:content="python:exceptFunc ('Test exception!')">Exists</html>"""
					   ,'<html>Exception: Test exception!</html>'
					   ,'Exception thrown during python path not handled!'
					   ,allowPythonPath=1
					   )
		
	def testPythonPathDisabled (self):
		self._runTest_ ("""<html tal:content="python:helloFunc ('Colin!')">Exists</html>"""
					   ,'<html>0</html>'
					   ,'Python path with allowPythonPath=false still expanded!'
					   ,allowPythonPath=0
					   )
		
	def testPythonPathFuncSuccess (self):
		self._runTest_ ("""<html tal:content="python:helloFunc ('Colin!')">Exists</html>"""
					   ,'<html>Hello Colin!</html>'
					   ,'Python path with function failed.'
					   ,allowPythonPath=1
					   )
					   
	def testPythonPathSliceSuccess (self):
		self._runTest_ ("""<html tal:repeat="num python:myList[2:4]" tal:content="num">Exists</html>"""
					   ,'<html>3</html><html>4</html>'
					   ,'Python path with slice failed.'
					   ,allowPythonPath=1
					   )
		
if __name__ == '__main__':
	unittest.main()
