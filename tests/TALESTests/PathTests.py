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
	return "Hello World"
	
def nestedFunction ():
	return {'nest': simpleFunction}
	
class PathTests (unittest.TestCase):
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

if __name__ == '__main__':
	unittest.main()

