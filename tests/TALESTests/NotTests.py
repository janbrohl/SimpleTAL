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

