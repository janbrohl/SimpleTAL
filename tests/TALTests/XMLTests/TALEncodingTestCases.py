#!/usr/bin/python
""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""

import unittest, os
import StringIO, codecs
import logging, logging.config

import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
isoDecoder = codecs.lookup ("iso8859-1")[1]
	
class TALEncodingTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'Testing this and that')
		self.context.addGlobal ('HighBC', isoDecoder ('This cost nothing, yep £0!')[0])
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testISOToUTF8 (self):
		utf8Pound = "\xc2\xa3"
		template = simpleTAL.compileXMLTemplate ('<?xml version="1.0" encoding="iso8859-1"?>\n<html>£3.12?  <b tal:replace="HighBC"></b></html>')
		file = StringIO.StringIO()
		template.expand (self.context, file, 'utf-8')
		result = file.getvalue()
		expectedResult = '<?xml version="1.0"?>\n<html>' + utf8Pound + "3.12?  This cost nothing, yep " + utf8Pound + "0!</html>"
		self.failUnless (result == expectedResult, "UTF8 Encoding failed.  \nResult was: " + result + "\nExpected result: " + expectedResult)
		
	def testISOToISO (self):
		template = simpleTAL.compileXMLTemplate ('<?xml version="1.0" encoding="iso8859-1"?>\n<html>£3.12?  <b tal:replace="HighBC"></b></html>')
		file = StringIO.StringIO()
		template.expand (self.context, file, 'iso8859-1')
		result = file.getvalue()
		expectedResult = '<?xml version="1.0" encoding="iso8859-1"?>\n<html>£3.12?  This cost nothing, yep £0!</html>'
		self.failUnless (result == expectedResult, "ISO Encoding failed.  \nResult was: " + result + "\nExpected result: " + expectedResult)
	
	def testUTF8ToISO (self):
		template = simpleTAL.compileXMLTemplate ('<?xml version="1.0"?>\n<html>\xc2\xa33.12?  <b tal:replace="HighBC"></b></html>')
		file = StringIO.StringIO()
		template.expand (self.context, file, 'iso8859-1')
		result = file.getvalue()
		expectedResult = '<?xml version="1.0" encoding="iso8859-1"?>\n<html>£3.12?  This cost nothing, yep £0!</html>'
		self.failUnless (result == expectedResult, "UTF8 -> ISO Encoding failed.  \nResult was: " + result + "\nExpected result: " + expectedResult)
		
if __name__ == '__main__':
	unittest.main()

