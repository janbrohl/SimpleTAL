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

