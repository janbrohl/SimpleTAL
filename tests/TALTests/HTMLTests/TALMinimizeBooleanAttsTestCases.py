#!/usr/bin/python
"""		Copyright (c) 2009 Colin Stewart (http://www.owlfish.com/)
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
import io
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
		self.context.addGlobal ('bob', 'bob')
		self.context.addGlobal ('disabled', 'disabled')
		self.context.addGlobal ('notdisabled', 'notdisabled')
		
	def _runTest_ (self, txt, result, errMsg="Error", minimizeBooleanAtts = 1):
		template = simpleTAL.compileHTMLTemplate (txt, minimizeBooleanAtts = minimizeBooleanAtts)
		file = io.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testTemplateWithBooleanAtt (self):
		self._runTest_ ('<html><input checked>Hello</html>'
								,'<html><input checked>Hello</html>'
								,"Template minimized boolean att failed.")
								
	def testTemplateWithBooleanAttWithBooleanDisabled (self):
		self._runTest_ ('<html><input checked>Hello</html>'
								,'<html><input checked="checked">Hello</html>'
								,"Template minimized boolean att failed to output full form with support disabled."
								, 0)
				
	def testTemplateWithFullAtt (self):
		self._runTest_ ('<html><input checked="checked">Hello</html>'
								,'<html><input checked>Hello</html>'
								,"Template full att failed.")
								
	def testTemplateWithFullAttWithBooleanDisabled (self):
		self._runTest_ ('<html><input checked="checked">Hello</html>'
								,'<html><input checked="checked">Hello</html>'
								,"Template full boolean att failed to output full form with support disabled."
								, 0)

	def testTemplateWithBadBooleanAtt (self):
		self._runTest_ ('<html><input checked="notchecked">Hello</html>'
								,'<html><input checked>Hello</html>'
								,"Template bad boolean att failed.")
								
	def testTALRemoveBooleanAtt (self):
		self._runTest_ ('<html><input disabled tal:attributes="disabled nothing">Hello</html>'
								,'<html><input>Hello</html>'
								,"TAL failed to remove minimized boolean tag")
	
	def testTALAddBooleanAtt (self):
		self._runTest_ ('<html><input tal:attributes="disabled disabled">Hello</html>'
								,'<html><input disabled>Hello</html>'
								,"TAL failed to add minimized boolean tag")
								
	def testTALBadBooleanAtt (self):
		self._runTest_ ('<html><input tal:attributes="disabled notdisabled">Hello</html>'
								,'<html><input disabled>Hello</html>'
								,"TAL failed to add with bad minimized boolean tag")
								
	def testTALNonBooleanAtt (self):
		self._runTest_ ('<html><input tal:attributes="bob bob">Hello</html>'
								,'<html><input bob="bob">Hello</html>'
								,"TAL failed to add non-boolean tag")
								
	def testTALBooleanAttSupportDisabled (self):
		self._runTest_ ('<html><input tal:attributes="disabled disabled">Hello</html>'
								,'<html><input disabled="disabled">Hello</html>'
								,"TAL failed to keep long form when support for minimized form disabled"
								,0)
								
	def testTemplateAllBooleanAtts (self):
		self._runTest_ ("""<html>
									<area nohref>
									<img ismap>
									<object declare></object>
									<input checked disabled readonly ismap>
									<select multiple disabled></select>
									<optgroup disabled></optgroup>
									<option selected disabled></option>
									<textarea disabled readonly></textarea>
									<button disabled></button>
									<script defer></script>"""
								,"""<html>
									<area nohref>
									<img ismap>
									<object declare></object>
									<input checked disabled readonly ismap>
									<select multiple disabled></select>
									<optgroup disabled></optgroup>
									<option selected disabled></option>
									<textarea disabled readonly></textarea>
									<button disabled></button>
									<script defer></script>"""
								,"Template failed to handle every boolean option")
								
if __name__ == '__main__':
	unittest.main()

