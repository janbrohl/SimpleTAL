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
	return "Hello"
	
def simpleFalseFunc ():
	return 0
			
class StringTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('top', 'Hello from the top')
		self.context.addGlobal ('alt', 'Wobble the way')
		self.context.addGlobal ('holder', {'helloFunc': simpleFunction
										  								,'falseFunc': simpleFalseFunc})		
		self.context.addGlobal ('version', 3.1)
		self.context.addGlobal ('uniString', u"Hello")
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))

	def testEmptyString (self):
		self._runTest_ ('<html tal:content="string:">Exists</html>'
					   ,'<html></html>'
					   ,'Empty string returned something!'
					   )
					   
	def testStaticString (self):
		self._runTest_ ('<html tal:content="string:Hello World!">Exists</html>'
					   ,'<html>Hello World!</html>'
					   ,'Static string didnt appear!'
					   )

	def testSingleVariable (self):
		self._runTest_ ('<html tal:content="string:$top">Exists</html>'
					   ,'<html>Hello from the top</html>'
					   ,'Single variable failed.'
					   )
					   
	def testStartVariable (self):
		self._runTest_ ('<html tal:content="string:$top of here">Exists</html>'
					   ,'<html>Hello from the top of here</html>'
					   ,'Start variable failed.'
					   )
					   
	def testMidVariable (self):
		self._runTest_ ('<html tal:content="string:Thoughts - $top eh?">Exists</html>'
					   ,'<html>Thoughts - Hello from the top eh?</html>'
					   ,'Mid variable failed.'
					   )

	def testEndVariable (self):
		self._runTest_ ('<html tal:content="string:Thought - $top">Exists</html>'
					   ,'<html>Thought - Hello from the top</html>'
					   ,'End variable failed.'
					   )
					   
	def testNumericVariable (self):
		self._runTest_ ('<html tal:content="string:Thought - $version">Exists</html>'
								   ,'<html>Thought - 3.1</html>'
								   ,'Numeric test variable failed.'
								   )
								   
	def testUnicodeVariable (self):
		self._runTest_ ('<html tal:content="string:Thought - ${uniString}">Exists</html>'
								   ,'<html>Thought - Hello</html>'
								   ,'Unicode test variable failed.'
								   )								   

	def testSinglePath (self):
		self._runTest_ ('<html tal:content="string:${top}">Exists</html>'
					   ,'<html>Hello from the top</html>'
					   ,'Single path failed.'
					   )
					   
	def testStartPath (self):
		self._runTest_ ('<html tal:content="string:${top} of here">Exists</html>'
					   ,'<html>Hello from the top of here</html>'
					   ,'Start path failed.'
					   )
					   
	def testMidPath (self):
		self._runTest_ ('<html tal:content="string:Thoughts - ${top}eh?">Exists</html>'
					   ,'<html>Thoughts - Hello from the topeh?</html>'
					   ,'Mid path failed.'
					   )

	def testEndPath (self):
		self._runTest_ ('<html tal:content="string:Thought - ${top}">Exists</html>'
					   ,'<html>Thought - Hello from the top</html>'
					   ,'End path failed.'
					   )

	def testMultiplePath (self):
		self._runTest_ ('<html tal:content="string:Thought - ${top} is here and ${no/such/path | string:recursive}">Exists</html>'
					   ,'<html>Thought - Hello from the top is here and recursive</html>'
					   ,'Multiple paths failed.'
					   )	
					   
	def testNoSuchPath (self):
		self._runTest_ ('<html tal:content="string:${no/such/path}">Exists</html>'
					   ,'<html></html>'
					   ,'No such path failed.'
					   )	
					   
	def testTrailingDollar (self):
		self._runTest_ ('<html tal:content="string:A trailing dollar: $">Exists</html>'
					   ,'<html>A trailing dollar: </html>'
					   ,'No such path failed.'
					   )

	def testDollarEscaping (self):
		self._runTest_ ('<html tal:content="string:$$A trailing $$dollar: $$">Exists</html>'
					   ,'<html>$A trailing $dollar: $</html>'
					   ,'No such path failed.'
					   )
					   
	def testPartialMissing (self):
		self._runTest_ ('<html tal:content="string: First bit here: ${alt} second bit not: ${nosuchname} there.">Exists</html>'
					   ,'<html>First bit here: Wobble the way second bit not:  there.</html>'
					   ,'Combination of non-existant variable and existing test failed.'
					   )
					   
if __name__ == '__main__':
	unittest.main()
