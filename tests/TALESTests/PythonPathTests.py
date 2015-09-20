#!/usr/bin/python
""" 	Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
		All rights reserved.
		
		Redistribution and use in source and binary forms, with or without
		modification, are permitted provided that the following conditions
		are met:
		1. Redistributions of source code must retain the above copyright
		   notice, this list of conditions and the following disclaimer.
		2. Redistributions in binary form must reproduce the above copyright
		   notice, this list of conditions and the following disclaimer in the
		   documentation and/or other materials provided with the distribution.
		3. The name of the author may not be used to endorse or promote products
		   derived from this software without specific prior written permission.
		
		THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
		IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
		OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
		IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
		INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
		NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
		DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
		THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
		THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		
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
	
def helloFunction ():
	return "Hello"
	
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
		self.context.addGlobal ('helloPath', simpleTALES.PathFunctionVariable(simpleFunction))
		self.context.addGlobal ('helloFunction', helloFunction)
		self.context.addGlobal ('myList', [1,2,3,4,5,6])
		self.context.addGlobal ('testing', 'testing')
		self.context.addGlobal ('map', {'test': 'maptest'})
		self.context.addGlobal ('data', {'one': 1, 'zero': 0})
		
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
					   
	def testPythonStringCompare (self):
		self._runTest_ ("""<html tal:condition="python: testing=='testing'">Passed.</html>"""
						,'<html>Passed.</html>'
						,'Python string compare failed.'
						,allowPythonPath=1
						)
						
	def testPythonPathFunc (self):
		self._runTest_ ("""<html tal:content="python: path ('map/test')">Passed.</html>"""
						,'<html>maptest</html>'
						,'Python path function call failed'
						,allowPythonPath=1
						)
						
	def testPythonStringFunc (self):
		self._runTest_ ("""<html tal:content="python: string ('Hello ${map/test} there')">Passed.</html>"""
						,'<html>Hello maptest there</html>'
						,'Python string function call failed'
						,allowPythonPath=1
						)
						
	def testPythonExistsFunc1 (self):
		self._runTest_ ("""<html tal:condition="python: exists ('map/test')">Passed.</html>"""
						,'<html>Passed.</html>'
						,'Python exists function call failed'
						,allowPythonPath=1
						)
						
	def testPythonExistsFunc2 (self):
		self._runTest_ ("""<html tal:condition="python: exists ('map/nosuchpath')">Passed.</html>"""
						,''
						,'Python exists function call failed'
						,allowPythonPath=1
						)
						
	def testPythonNocallFunc (self):
		self._runTest_ ("""<html tal:condition="python: callable (nocall ('helloFunc'))">Passed.</html>"""
						,'<html>Passed.</html>'
						,'Python nocall function call failed'
						,allowPythonPath=1
						)
						
	def testPythonPathFuncWithFunc (self):
		self._runTest_ ("""<html tal:condition="python: path ('helloFunction')=='Hello'">Passed.</html>"""
						,'<html>Passed.</html>'
						,'Python path function using a function failed'
						,allowPythonPath=1
						)
	
	def testPythonPathFuncWithPath (self):
		self._runTest_ ("""<html tal:condition="python: helloPath ('helloFunction')=='Hello helloFunction'">Passed.</html>"""
						,'<html>Passed.</html>'
						,'Python path function wrapped in a PathFunctionVariable failed'
						,allowPythonPath=1
						)
						
	def testTestFunctionDefault (self):
		self._runTest_ ("""<html tal:condition="python: test (path ('data/one'))">Passed.</html>"""
						,'<html>Passed.</html>'
						,'Test function failed to use default.'
						,allowPythonPath=1
						)

	def testTestFunctionTwoArgs (self):
		self._runTest_ ("""<html tal:condition="python: test (0,1)">Passed.</html>"""
						,''
						,'Test function failed to use default of false.'
						,allowPythonPath=1
						)
						
	def testTestFunctionThreeArgs (self):
		self._runTest_ ("""<html tal:content="python: test (0,1,2)">Passed.</html>"""
						,'<html>2</html>'
						,'Test function failed to use default.'
						,allowPythonPath=1
						)
						
	def testTestFunctionFiveArgs (self):
		self._runTest_ ("""<html tal:content="python: test (0,1,0,2,5)">Passed.</html>"""
						,'<html>5</html>'
						,'Test function failed to use default.'
						,allowPythonPath=1
						)
						
if __name__ == '__main__':
	unittest.main()
