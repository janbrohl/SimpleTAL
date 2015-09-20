#!/usr/bin/python
""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""

import unittest, os, codecs
import StringIO
import logging, logging.config

import simpleTALUtils, simpleTALES, simpleTAL

macroTemplate = simpleTAL.compileHTMLTemplate ("""<html>
<body metal:define-macro="one">World is <i metal:define-slot="blue">White</i></body>
</html>
""")

#print "Macro is: %s" % str (macroTemplate)

class MacroExpansionTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		entry = """Some structure: <b tal:content="weblog/subject"></b>"""
		
		weblog = {'subject': 'Test subject', 'entry': entry}
		
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('mac', macroTemplate)
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		self.context.addGlobal ('weblog', weblog)
		
	def _runTest_ (self, template, txt, result, errMsg="Error"):
		realResult = simpleTALUtils.ExpandMacros (self.context, template)
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
			
	def testMacroExpansionSlots (self):
		txt = '<html><div metal:use-macro="mac/macros/one">Hello<b metal:fill-slot="blue">Blue</b></div></html>'
		template = simpleTAL.compileHTMLTemplate (txt)
		self._runTest_ (template
									 ,txt
									 ,'<html><body metal:use-macro="mac/macros/one">World is <b metal:fill-slot="blue">Blue</b></body></html>'
									 ,'Expasion with slots failed.')
									 
	def testXMLMacroExpansionSlots (self):
		txt = '<?xml version="1.0" encoding="utf8"?>\n<html><div metal:use-macro="mac/macros/one">Hello<b metal:fill-slot="blue">Blue</b></div></html>'
		template = simpleTAL.compileXMLTemplate (txt)
		self._runTest_ (template
									 ,txt
									 ,'<?xml version="1.0" encoding="iso8859-1"?>\n<html><body metal:use-macro="mac/macros/one">World is <b metal:fill-slot="blue">Blue</b></body></html>'
									 ,'Expasion with slots failed.')
		
if __name__ == '__main__':
	unittest.main()