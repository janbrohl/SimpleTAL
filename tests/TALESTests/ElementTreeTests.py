#!/usr/bin/python
""" 	Copyright (c) 20045Colin Stewart (http://www.owlfish.com/)
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

try:
	from simpletal import simpleElementTree
	
	ELEMENT_TREE_SUPPORT = 1
except:
	ELEMENT_TREE_SUPPORT = 0

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()

def simpleFunction (param):
	return "Hello %s" % param
	
def helloFunction ():
	return "Hello"
				
class ElementTreeTestCases (unittest.TestCase):
	def setUp (self):
		pass
			
	def _runTest_ (self, txt, result, errMsg="Error", allowPythonPath=0):
		if (not ELEMENT_TREE_SUPPORT):
			logging.warn ("No ElementTree support found, skipping test.")
			return
			
		self.context = simpleTALES.Context(allowPythonPath=allowPythonPath)
		self.context.addGlobal ('top', 'Hello from the top')
		self.context.addGlobal ('helloFunc', simpleFunction)
		self.context.addGlobal ('helloPath', simpleTALES.PathFunctionVariable(simpleFunction))
		self.context.addGlobal ('helloFunction', helloFunction)
		self.context.addGlobal ('myList', [1,2,3,4,5,6])
		self.context.addGlobal ('testing', 'testing')
		self.context.addGlobal ('map', {'test': 'maptest'})
		self.context.addGlobal ('data', {'one': 1, 'zero': 0})
		
		testXML = '<?xml version="1.0" encoding="utf-8"?><root><title type="Example">This is a test</title></root>'
		xmlTree = simpleElementTree.parseFile (StringIO.StringIO (testXML))
		self.context.addGlobal ("xml", xmlTree)
		
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))

	def testNormalTree (self):
		self._runTest_ ("""<html tal:content="xml/title>Exists</html>"""
					   ,'<html>This is a test</html>'
					   ,'Simple Element Tree test failed.'
					   ,allowPythonPath=1
					   )
		
	def testPythonPathTree (self):
		self._runTest_ ("""<html tal:content="python:path ('xml/title')">Exists</html>"""
					   ,'<html>This is a test</html>'
					   ,'Python path use of Element Tree failed.'
					   ,allowPythonPath=1
					   )