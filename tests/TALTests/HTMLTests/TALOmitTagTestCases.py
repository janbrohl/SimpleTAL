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

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
class TALOmitTagTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('link', 'www.owlfish.com')
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testOmitTagTrue (self):
		self._runTest_ ('<html tal:omit-tag="link" href="owlfish.com">Hello</html>'
										,'Hello'
										,"Omit tag, true, failed.")
										
	def testOmitTagNoArg (self):
		self._runTest_ ('<html tal:omit-tag href="owlfish.com">Hello</html>'
										,'Hello'
										,"Omit tag, no arg, failed.")
		
	def testOmitTagEmptyArg (self):
		self._runTest_ ('<html tal:omit-tag="" href="owlfish.com">Hello</html>'
										,'Hello'
										,"Omit tag, empty arg, failed.")
						
	def testOmitTagFalse (self):
		self._runTest_ ('<html tal:omit-tag="wibble" href="owlfish.com">Hello</html>'
										,'<html href="owlfish.com">Hello</html>'
										,"Omit tag, false, failed.")
						

if __name__ == '__main__':
	unittest.main()

