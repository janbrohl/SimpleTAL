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
	
class DefineSlotsTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('link', 'www.owlfish.com')
		self.context.addGlobal ('needsQuoting', """Does "this" & work?""")
		
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
	
	def _runCompileTest_ (self, txt, result, errMsg="Error"):
		try:
			macroTemplate = simpleTAL.compileHTMLTemplate (txt)
		except simpleTAL.TemplateParseException, e:
			self.failUnless (str (e) == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, str(e), result, pageTemplate))
			return
		self.fail ("Expected exception '%s' during compile - but got no exception" % result)				
					
	def testSingleSlot (self):
		self._runTest_ ('<html><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue">blue</b> After</div></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i> here</body></html>'
										,'<html><div class="funny">Before <i>white</i> After</div></html>'
										,"Single slot expansion failed.")
										
	def testDoubleSlot (self):
		self._runTest_ ('<html><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue">blue</b> After <a metal:define-slot="red">red</a></div></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i> here <b metal:fill-slot="red">black</b></body></html>'
										,'<html><div class="funny">Before <i>white</i> After <b>black</b></div></html>'
										,"Double slot expansion failed.")
		
	def testDoubleOneDefaultSlot (self):
		self._runTest_ ('<html><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue">blue</b> After <a metal:define-slot="red">red</a></div></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i> here <b metal:fill-slot="purple">purple</b></body></html>'
										,'<html><div class="funny">Before <i>white</i> After <a>red</a></div></html>'
										,"Double slot with default, expansion failed.")
										
	def testDoubleMacroDefaultSlot (self):
		self._runTest_ ('<html><p metal:define-macro="two">Internal macro, colour blue: <b metal:define-slot="blue">blue</b></p><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue">blue</b> After <a metal:use-macro="site/macros/two">Internal</a></div></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i></body></html>'
										,'<html><div class="funny">Before <i>white</i> After <p>Internal macro, colour blue: <b>blue</b></p></div></html>'
										,"Nested macro with same slot name.")

	def testDoubleMacroDoubleFillSlot (self):
		self._runTest_ ('<html><p metal:define-macro="two">Internal macro, colour blue: <b metal:define-slot="blue">blue</b></p><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue">blue</b> After <a metal:use-macro="site/macros/two">Internal<p metal:fill-slot="blue">pink!</p></a> finally outer blue again: <a metal:define-slot="blue">blue goes here</a></div></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i></body></html>'
										,'<html><div class="funny">Before <i>white</i> After <p>Internal macro, colour blue: <p>pink!</p></p> finally outer blue again: <i>white</i></div></html>'
										,"Nested macro with same slot name and slot being used failed.")

	def testSingleSlotDefaultTAL (self):
		self._runTest_ ('<html><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue" tal:content="test">blue</b> After</div></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt here</body></html>'
										,'<html><div class="funny">Before <b>testing</b> After</div></html>'
										,"Slot defaulting that holds TAL failed.")

	def testSingleSlotPassedInTAL (self):
		self._runTest_ ('<html><div metal:define-macro="one" class="funny">Before <b metal:define-slot="blue" tal:content="test">blue</b> After</div></html>'
										,'<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue" tal:content="needsQuoting" tal:attributes="href link">boo</i> here</body></html>'
										,'<html><div class="funny">Before <i href="www.owlfish.com">Does "this" &amp; work?</i> After</div></html>'
										,"Slot filled with TAL failed.")
										
if __name__ == '__main__':
	unittest.main()
