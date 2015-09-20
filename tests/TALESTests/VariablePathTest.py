#!/usr/bn/python
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

def simpleFunction ():
	return "Hello World"
	
def nestedFunction ():
	return {'nest': simpleFunction}
		
def pathFunction (thePath):
	return thePath
	
class PathTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('colours', {'blue': 'The sea is blue', 'red': 'The ball is red', 'green': 'The grass is green'})
		self.context.addGlobal ('aList', ['blue', 'green'])
		self.context.addGlobal ('goodColour', 'goodColourPath')
		self.context.addGlobal ('goodColourPath', 'Black is good')
		self.context.addGlobal ('noSuchColour', 'pink')	
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
			
	def testRepeatVariablePath (self):
		self._runTest_ ('<html><ul><li tal:repeat="colour aList" tal:content="colours/?colour">List</li></ul></html>'
					   ,'<html><ul><li>The sea is blue</li><li>The grass is green</li></ul></html>'
					   ,'Path variable during repeat failed.'
					   )
					   
	def testLocalVariablePath (self):
		self._runTest_ ('<html><p tal:define="one string:red">It is red: <b tal:content="colours/?one"></b></p></html>'
						,'<html><p>It is red: <b>The ball is red</b></p></html>'
						,'Local variable path failed.'
						)
						
	def testGlobalVariablePath (self):
		self._runTest_ ('<html><p tal:content="?goodColour"></p></html>'
						,'<html><p>Black is good</p></html>'
						,'Global variable path failed.'
						)
						
	def testNoSuchVariablePath (self):
		self._runTest_ ('<html><p tal:content="?badColour"></p></html>'
					   ,'<html><p></p></html>'
					   ,'No such variable failed.'
					   )
					   
	def testNoSuchVariablePath2 (self):
		self._runTest_ ('<html><p tal:content="colours/?noSuchColour"></p></html>'
					   ,'<html><p></p></html>'
					   ,'No such variable2 failed.'
					   )				