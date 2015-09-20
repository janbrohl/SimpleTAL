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
	
class METALNameSpaceTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, macros, page, result, errMsg="Error"):
		macroTemplate = simpleTAL.compileHTMLTemplate (macros)
		#print "Macro template: " + str (macroTemplate)
		pageTemplate = simpleTAL.compileHTMLTemplate (page)
		self.context.addGlobal ("site", macroTemplate)
		self.context.addGlobal ("here", pageTemplate)
		file = StringIO.StringIO ()
		pageTemplate.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in macro: %s \npage: %s\ngot back %s \nexpected %s\n" % (errMsg, macros, page, realResult, result))
	
	# Test that rebinding the namespaces works		
	def testSingleBindNoCommands (self):
		self._runTest_ ('<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue">blue</b> After</div></html>'
										,'<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i> here</body></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i> here</body></html>'
										,"Single Bind, commands, failed.")
										
	def testSingleBindCommands (self):
		self._runTest_ ('<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><div newmetal:define-macro="one" class="funny">Before <b newmetal:define-slot="blue">blue</b> After</div></html>'
										,'<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><body newmetal:use-macro="site/macros/one">Nowt <i newmetal:fill-slot="blue">white</i> here</body></html>'
										,'<html><div class="funny">Before <i>white</i> After</div></html>'
										,"Single Bind, commands, failed.")
										
if __name__ == '__main__':
	unittest.main()

