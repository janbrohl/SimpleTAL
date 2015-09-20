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
	
class TALAttributesTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('link', 'www.owlfish.com')
		self.context.addGlobal ('needsQuoting', """Does "this" work?""")
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testAddingAnAttribute (self):
		self._runTest_ ('<html tal:attributes="link link" href="owlfish.com">Hello</html>'
										,'<html link="www.owlfish.com" href="owlfish.com">Hello</html>'
										,"Addition of attribute 'link' failed.")
		
	def testRemovingAnAttribute (self):
		self._runTest_ ('<html class="test" tal:attributes="href nothing" href="owlfish.com">Hello</html>'
										,'<html class="test">Hello</html>'
										,"Removal of attribute 'href' failed.")
						
	def testDefaultAttribute (self):
		self._runTest_ ('<html class="test" tal:attributes="href default" href="owlfish.com">Hello</html>'
										,'<html class="test" href="owlfish.com">Hello</html>'
										,"Defaulting of attribute 'href' failed.")

	def testMultipleAttributes (self):
		self._runTest_ ('<html old="still here" class="test" tal:attributes="href default;class nothing;new test" href="owlfish.com">Hello</html>'
										,'<html new="testing" old="still here" href="owlfish.com">Hello</html>'
										,"Setting multiple attributes at once failed.")
										
	def testAttributeEscaping (self):
		self._runTest_ ('<html existingAtt="&quot;Testing&quot;" tal:attributes="href needsQuoting">Hello</html>'
										,"""<html href="Does &quot;this&quot; work?" existingatt="&quot;Testing&quot;">Hello</html>"""
										,"Escaping of new attributes failed.")
		
						

if __name__ == '__main__':
	unittest.main()

