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

def simpleFunction ():
	return "Hello World"
	
def nestedFunction ():
	return {'nest': simpleFunction}
		
def pathFunction (thePath):
	return thePath
	
class CallRecorder:
	def __init__ (self):
		self.called = 0
		
	def simpleFunction (self):
		self.called += 1
		return "Hello"
	
class PathTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.recorder = CallRecorder()
		self.context.addGlobal ('top', 'Hello from the top')
		self.context.addGlobal ('alt', 'Wobble the way')
		self.context.addGlobal ('theMap', {'top': 'Hello', 'onelevel': {'top': 'Bye'}})
		self.context.addGlobal ('funcMap', {'simple': simpleFunction, 'nested': nestedFunction, 'pathFunc': simpleTALES.PathFunctionVariable (pathFunction)})
		self.context.addGlobal ('topFunc', simpleFunction)
		self.context.addGlobal ('pathFunc', simpleTALES.PathFunctionVariable (pathFunction))
		self.context.addGlobal ('cacheFunc', simpleTALES.CachedFuncResult (self.recorder.simpleFunction))
		self.context.addGlobal ('alist', [{'a': 'An A', 'b': 'A B'},"Hello!"])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
		
	def _runCacheTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
		self.failUnless (self.recorder.called == 1, 'Recorder shows function was called %s times!' % str (self.recorder.called))
			
	def testSimpleTopPath (self):
		self._runTest_ ('<html tal:replace="top">Top</html>'
					   ,'Hello from the top'
					   ,'Simple top level path failed.'
					   )
					   
	def testOneLevelMap (self):
		self._runTest_ ('<html tal:replace="theMap/top">Map</html>'
					   ,'Hello'
					   ,'One level deep map access failed.'
					   )
					   
	def testTwoLevelMap (self):
		self._runTest_ ('<html tal:replace="theMap/onelevel/top">Map</html>'
					   ,'Bye'
					   ,'Two level deep map access failed.'
					   )		
	
	def testOneLevelFuncMap (self):
		self._runTest_ ('<html tal:replace="funcMap/simple">Map</html>'
					   ,'Hello World'
					   ,'One level deep function access failed.'
					   )

	def testTwoLevelFuncMap (self):
		self._runTest_ ('<html tal:replace="funcMap/nested/nest">Map</html>'
					   ,'Hello World'
					   ,'Two level deep function access failed.'
					   )
					   
	def testTopLevelFunc (self):
		self._runTest_ ('<html tal:replace="topFunc">Map</html>'
					   ,'Hello World'
					   ,'Top level function access failed.'
					   )

	def testFirstORPath (self):
		self._runTest_ ('<html tal:replace="top | alt">hmm</html>'
					   ,'Hello from the top'
					   ,'First valid path was not selected.'
					   )
					   					   
	def testSecondORPath (self):
		self._runTest_ ('<html tal:replace="thingy | alt">hmm</html>'
					   ,'Wobble the way'
					   ,'Second valid path was not selected.'
					   )
					   
	def testImbalancedQuoteOne (self):
		self._runTest_ ('<html tal:replace=alt">hmm</html>'
					   ,'Wobble the way'
					   ,'Trailing quote was not handled'
					   )
					   
	def testImbalancedQuoteTwo (self):
		self._runTest_ ('<html tal:replace="alt>hmm</html>'
					   			,'Wobble the way'
					   			,'Trailing quote was not handled'
					   			)
					   
	def testImbalancedQuoteThree (self):
		self._runTest_ ("<html tal:replace=alt'>hmm</html>"
					   ,'Wobble the way'
					   ,'Trailing quote was not handled'
					   )
					   
	def testImbalancedQuoteFour (self):
		self._runTest_ ("<html tal:replace='alt>hmm</html>"
					   ,'Wobble the way'
					   ,'Trailing quote was not handled'
					   )
					   
	def testPathFunctionNoParams (self):
		self._runTest_ ('<html tal:content="pathFunc">hmm</html>'
						,'<html></html>'
						,'Path Function with no parameters failed.'
						)
						
	def testPathFunctionWithOnePath (self):
		self._runTest_ ('<html tal:content="pathFunc/firstPath">hmm</html>'
						,'<html>firstPath</html>'
						,'Path Function with one parameter failed.'
						)
						
	def testPathFunctionWithTwoPath (self):
		self._runTest_ ('<html tal:content="pathFunc/firstPath/second">hmm</html>'
						,'<html>firstPath/second</html>'
						,'Path Function with two parameters failed.'
						)
						
	def testPathFunctionWithOnePathOneDeep (self):
		self._runTest_ ('<html tal:content="funcMap/pathFunc/firstPath">hmm</html>'
						,'<html>firstPath</html>'
						,'Path Function with one parameter, nested one deep, failed.'
						)
						
	def testAList (self):
		self._runTest_ ('<html tal:content="alist/0/a">hmm</html>'
						,'<html>An A</html>'
						,'Index into list then dictionary failed.'
						)
						
	def testAList2ndItem (self):
		self._runTest_ ('<html tal:content="alist/1">hmm</html>'
						,'<html>Hello!</html>'
						,'Index into list failed.'
						)
						
	def testAListNoSuchItem (self):
		self._runTest_ ('<html tal:content="alist/2">hmm</html>'
						,'<html></html>'
						,'Index past end of list failed.'
						)
						
	def testCachedFuction (self):
		self._runCacheTest_ ('<b tal:content="cacheFunc"></b><i tal:replace="cacheFunc"></i>'
							,'<b>Hello</b>Hello'
							,"Cached function didn't return as expected."
							)

if __name__ == '__main__':
	unittest.main()

