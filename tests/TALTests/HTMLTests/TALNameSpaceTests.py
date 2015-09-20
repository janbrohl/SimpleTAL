#!/usr/bin/python
"""		Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
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
	
class TALNameSpaceTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
	
	def _runErrTest_ (self, txt, result, errMsg="Error"):
		try:
			template = simpleTAL.compileHTMLTemplate (txt)
		except simpleTAL.TemplateParseException, e:
			realResult = str (e)
			self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back exception %s \nexpected exception %s\n" % (errMsg, txt, realResult, result))
			return
		self.fail ("No exception thrown!")					

	# Test that rebinding the namespaces works		
	def testSingleBindNoCommands (self):
		self._runTest_ ('<html xmlns:newtal="http://xml.zope.org/namespaces/tal"><body tal:condition="default">Hello</body></html>'
										,'<html><body tal:condition="default">Hello</body></html>'
										,'Binding of namespace failed.')
		
	def testSingleBind (self):
		self._runTest_ ('<html xmlns:newtal="http://xml.zope.org/namespaces/tal"><body newtal:condition="default">Hello</body></html>'
										,'<html><body>Hello</body></html>'
										,'Binding of namespace failed.')

	def testSingleNestedBind (self):
		self._runTest_ ('<html><body xmlns:newtal="http://xml.zope.org/namespaces/tal"><p newtal:condition="default">Hello</p><b tal:content="test">default content</b></body><b tal:content="test">default content</b></html>'
										,'<html><body><p>Hello</p><b tal:content="test">default content</b></body><b>testing</b></html>'
										,'Binding of namespace failed to nest correctly')						

	def testDoubleNestedBind (self):
		self._runTest_ ('<html><body xmlns:newtal="http://xml.zope.org/namespaces/tal"><p newtal:condition="default">Hello</p><div xmlns:new2tal="http://xml.zope.org/namespaces/tal"><b tal:content="test">default content</b><i new2tal:content="test">default</i></div></body><b tal:content="test">default content</b></html>'
										,'<html><body><p>Hello</p><div><b tal:content="test">default content</b><i>testing</i></div></body><b>testing</b></html>'
										,'Binding of namespace failed to nest correctly with 2 nests')						

	def testOtherNameSpaces (self):
		self._runTest_ ('<html xmlns:newtal="http://no.such.name/"><body newtal:condition="default">Hello</body></html>'
										,'<html xmlns:newtal="http://no.such.name/"><body newtal:condition="default">Hello</body></html>'
										,'Namespaces removed!')
											
	# Now test exceptions
	def testDefaultTALNameSpace (self):
		self._runErrTest_ ('<html xmlns="http://xml.zope.org/namespaces/tal"><body newtal:condition="default">Hello</body></html>'
											,'[<html xmlns="http://xml.zope.org/namespaces/tal">] Can not use TAL name space by default, a prefix must be provided.'
											,'Namespaces removed!')


if __name__ == '__main__':
	unittest.main()

