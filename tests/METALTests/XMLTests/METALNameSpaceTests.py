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
	
class METALNameSpaceTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		
	def _runTest_ (self, macros, page, result, errMsg="Error"):
		macroTemplate = simpleTAL.compileXMLTemplate (macros)
		#print "Macro template: " + str (macroTemplate)
		pageTemplate = simpleTAL.compileXMLTemplate (page)
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
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body metal:use-macro="site/macros/one">Nowt <i metal:fill-slot="blue">white</i> here</body></html>'
										,"Single Bind, commands, failed.")
										
	def testSingleBindCommands (self):
		self._runTest_ ('<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><div newmetal:define-macro="one" class="funny">Before <b newmetal:define-slot="blue">blue</b> After</div></html>'
										,'<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><body newmetal:use-macro="site/macros/one">Nowt <i newmetal:fill-slot="blue">white</i> here</body></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html><div class="funny">Before <i>white</i> After</div></html>'
										,"Single Bind, commands, failed.")
	
	# Test to ensure that using elements in the metal namespace omits tags
	def testMETALEmlement (self):
		self._runTest_ ('<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><newmetal:div newmetal:define-macro="one" class="funny">Before <b newmetal:define-slot="blue">blue</b> After</newmetal:div></html>'
										,'<html xmlns:newmetal="http://xml.zope.org/namespaces/metal"><body newmetal:use-macro="site/macros/one">Nowt <newmetal:block newmetal:fill-slot="blue">white</newmetal:block> here</body></html>'
										,'<?xml version="1.0" encoding="iso-8859-1"?>\n<html>Before white After</html>'
										,"Single Bind, commands, failed.")
										
if __name__ == '__main__':
	unittest.main()

