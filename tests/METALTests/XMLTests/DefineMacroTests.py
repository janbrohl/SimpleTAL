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

try:
    # Is PyXML's LexicalHandler available? 
    from xml.sax.saxlib import LexicalHandler
    use_lexical_handler = 1
except ImportError:
    use_lexical_handler = 0

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
pageTemplate = simpleTAL.compileXMLTemplate ("""<html>
<body metal:use-macro="site/macros/one">
<h1 metal:fill-slot="title">Expansion of macro one</h1>
</body>
<br/>
</html>""")

class DefineMacroTests (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('link', 'www.owlfish.com')
		self.context.addGlobal ('needsQuoting', """Does "this" work?""")
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		macroTemplate = simpleTAL.compileXMLTemplate (txt)
		self.context.addGlobal ("site", macroTemplate)
		file = StringIO.StringIO ()
		pageTemplate.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, pageTemplate))
	
	def _runCompileTest_ (self, txt, result, errMsg="Error"):
		try:
			macroTemplate = simpleTAL.compileXMLTemplate (txt)
		except simpleTAL.TemplateParseException, e:
			self.failUnless (str (e) == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, str(e), result, pageTemplate))
			return
		self.fail ("Expected exception '%s' during compile - but got no exception" % result)				
					
	def testSingleMacroDefinition (self):
		if (use_lexical_handler):
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<div class="funny">No slots here</div>\n<br />\n</html>'
		else:
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<div class="funny">No slots here</div>\n<br></br>\n</html>'
			
		self._runTest_ ('<html><div metal:define-macro="one" class="funny">No slots here</div></html>'
										,result
										,"Single macro with no slots failed.")
		
	def testTwoMacroDefinition (self):
		if (use_lexical_handler):
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<div class="funny">No slots here</div>\n<br />\n</html>'
		else:
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<div class="funny">No slots here</div>\n<br></br>\n</html>'
			
		self._runTest_ ('<html><body metal:define-macro="two">A second macro</body><div metal:define-macro="one" class="funny">No slots here</div></html>'
										,result
										,"Two macros with no slots failed.")
										
	def testNestedMacroDefinition (self):
		if (use_lexical_handler):
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<body>A second macro</body>\n<br />\n</html>'
		else:
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<body>A second macro</body>\n<br></br>\n</html>'
			
		self._runTest_ ('<html><div metal:define-macro="two" class="funny"><body metal:define-macro="one">A second macro</body>No slots here</div></html>'
										,result
										,"Nested macro with no slots failed.")
										
	def testDuplicateMacroDefinition (self):
		self._runCompileTest_ ('<html><div metal:define-macro="one" class="funny"><body metal:define-macro="one">A second macro</body>No slots here</div></html>'
								,'[<body metal:define-macro="one">] Macro name one is already defined!'
								,"Duplicate macro failed to error.")										

	def testMacroTALDefinition (self):
		if (use_lexical_handler):
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<p>testing</p>\n<br />\n</html>'
		else:
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<p>testing</p>\n<br></br>\n</html>'
			
		self._runTest_ ('<html><p metal:define-macro="one" tal:content="test">Wibble</p></html>'
						, result
						,"TAL Command on a macro failed.")
						
	def testSingletonMacros (self):
		if (use_lexical_handler):
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<p>Wibble<br /></p>\n<br />\n</html>'
		else:
			result = '<?xml version="1.0" encoding="iso-8859-1"?>\n<html>\n<p>Wibble<br></br></p>\n<br></br>\n</html>'
			
		self._runTest_ ('<html><p metal:define-macro="one">Wibble<br/></p></html>'
						,result
						,"Singleton inside slot failed.")
	
if __name__ == '__main__':
	unittest.main()
