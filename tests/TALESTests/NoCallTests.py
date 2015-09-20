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

class CallRecorder:
	def __init__ (self):
		self.called = 0
		
	def simpleFunction (self):
		self.called = 1
		return "Hello"
			
class NoCallTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.recorder = CallRecorder()
		self.context.addGlobal ('top', 'Hello from the top')
		self.context.addGlobal ('alt', 'Wobble the way')
		self.context.addGlobal ('holder', {'recorder': self.recorder.simpleFunction})
		
	def _runTest_ (self, txt, result, errMsg="Error", expectedRecorderVal=0):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
		self.failUnless (self.recorder.called == expectedRecorderVal, 'Call recorder detected that the call recorder object has state %s' % str (self.recorder.called))
			
	def testNoCallString (self):
		self._runTest_ ('<html tal:define="test nocall:top"><b tal:condition="exists:test">Exists</b></html>'
					   ,'<html><b>Exists</b></html>'
					   ,'Binding string using nocall failed.'
					   )
					   
	def testNoCallRecorder (self):
		self._runTest_ ('<html tal:define="test nocall:holder/recorder"><b tal:condition="exists:test">Exists</b></html>'
					   ,'<html><b>Exists</b></html>'
					   ,'Binding function using nocall failed.'
					   )
					   
	def testNoCallORPath (self):
		self._runTest_ ('<html tal:define="test nocall:holder/recorder | top"><b tal:condition="exists:test">Exists</b></html>'
					   ,'<html><b>Exists</b></html>'
					   ,'Binding function using nocall as first part of path failed'
					   )
		
	def testNoCallORPathTwo (self):
		self._runTest_ ('<html tal:define="test no/such/path | nocall:holder/recorder"><b tal:condition="exists:test">Exists</b></html>'
					   ,'<html><b>Exists</b></html>'
					   ,'Binding function using nocall as second part of path failed'
					   )
					   					   
	def testNoCallRecorderInfra (self):
		self._runTest_ ('<html tal:define="test holder/recorder"><b tal:condition="exists:test">Exists</b></html>'
					   ,'<html><b>Exists</b></html>'
					   ,'Recorder failed to note call'
					   ,1
					   )
					   					   	
if __name__ == '__main__':
	unittest.main()

