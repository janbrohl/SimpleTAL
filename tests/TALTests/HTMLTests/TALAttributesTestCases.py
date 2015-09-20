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
	
class TALAttributesTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('link', 'www.owlfish.com')
		self.context.addGlobal ('needsQuoting', """Does "this" work?""")
		self.context.addGlobal ('number', 5)
		self.context.addGlobal ('uniQuote', u'Does "this" work?')
		self.context.addGlobal ('anotherdefault', {'inhere': simpleTALES.DEFAULTVALUE})
		
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
										
	def testAnotherDefaultAttribute (self):
		self._runTest_ ('<html class="test" tal:attributes="href anotherdefault/inhere" href="owlfish.com">Hello</html>'
										,'<html class="test" href="owlfish.com">Hello</html>'
										,"Defaulting of attribute 'href' failed.")

	def testMultipleAttributes (self):
		self._runTest_ ('<html old="still here" class="test" tal:attributes="href default;class nothing;new test" href="owlfish.com">Hello</html>'
										,'<html new="testing" old="still here" href="owlfish.com">Hello</html>'
										,"Setting multiple attributes at once failed.")

	def testMultipleAttributesSpace (self):
		self._runTest_ ('<html old="still here" class="test" tal:attributes="href default ; class string:Hello there; new test" href="owlfish.com">Hello</html>'
										,'<html class="Hello there" new="testing" old="still here" href="owlfish.com">Hello</html>'
										,"Setting multiple attributes at once, with spaces between semi-colons, failed.")

	def testMultipleAttributesEscaped (self):
		self._runTest_ ('<html old="still &quot; here" class="test" tal:attributes="href default ; class string: Semi-colon;;test;new test " href="owlfish.com">Hello</html>'
										,'<html class="Semi-colon;test" new="testing" old="still &quot; here" href="owlfish.com">Hello</html>'
										,"Setting multiple attributes at once, with spaces between semi-colons, failed.")

	def testAttributeEscaping (self):
		self._runTest_ ('<html existingAtt="&quot;Testing&quot;" tal:attributes="href needsQuoting">Hello</html>'
										,"""<html href="Does &quot;this&quot; work?" existingatt="&quot;Testing&quot;">Hello</html>"""
										,"Escaping of new attributes failed.")
										
	def testNumberAttributeEscaping (self):
		self._runTest_ ('<html existingAtt="&quot;Testing&quot;" tal:attributes="href number">Hello</html>'
						,"""<html href="5" existingatt="&quot;Testing&quot;">Hello</html>"""
						,"Escaping of new attributes failed.")
		
	def testNumberAttributeEscaping (self):
		self._runTest_ ('<html existingAtt="&quot;Testing&quot;" tal:attributes="href uniQuote">Hello</html>'
						,"""<html href="Does &quot;this&quot; work?" existingatt="&quot;Testing&quot;">Hello</html>"""
						,"Escaping of new attributes failed.")
						
	def testOriginalAttributes (self):
		self._runTest_ ('<html existingAtt="&quot;Testing&quot;" tal:attributes="newAtt attrs/existingatt" tal:content="attrs/existingatt">Hello</html>'
						,"""<html newAtt="&quot;Testing&quot;" existingatt="&quot;Testing&quot;">"Testing"</html>"""
						,"Accessing existing attributes failed.")
						
	def testMultipleOriginalAttributes (self):
		self._runTest_ ('<html one="Value One" two="Value two" three="Value three" tal:attributes="four attrs/three" tal:content="attrs/one">Hello</html>'
						,"""<html four="Value three" one="Value One" two="Value two" three="Value three">Value One</html>"""
						,"Accessing multiple existing attributes failed.")
						
	# HTML Attributes are case insensitive.
#=======================================
#	def testAttributeCase (self):
#		self._runTest_ ('<html HREF="Testing" tal:attributes="HREF test">Hello</html>'
#						,"""<html href="testing">Hello</html>"""
#						,"HTML Attributes not treated as case insensitive.")
#=======================================
	


if __name__ == '__main__':
	unittest.main()

