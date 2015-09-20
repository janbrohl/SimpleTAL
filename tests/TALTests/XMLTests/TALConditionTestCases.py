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
	
class TALConditionTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileXMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testConditionDefault (self):
		self._runTest_ ('<html tal:condition="default">Hello</html>', '<?xml version="1.0" encoding="iso8859-1"?>\n<html>Hello</html>', "Condition 'default' did not evaluate to true")
		
	def testConditionExists (self):
		self._runTest_ ('<html tal:condition="test">Hello</html>'
						, '<?xml version="1.0" encoding="iso8859-1"?>\n<html>Hello</html>', 'Condition for something that exists evaluated false')
						
	def testConditionNothing (self):
		self._runTest_ ('<html tal:condition="nothing">Hello</html>'
						, '<?xml version="1.0" encoding="iso8859-1"?>\n', 'Condition nothing evaluated to true')

	def testConditionMissing (self):
		self._runTest_ ('<html tal:condition="thisdoesnotexists">Hello</html>'
						, '<?xml version="1.0" encoding="iso8859-1"?>\n', 'Condition for something that does not exist evaluated to true')
						

if __name__ == '__main__':
	unittest.main()

