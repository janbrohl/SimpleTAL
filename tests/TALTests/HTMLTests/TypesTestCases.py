#!/usr/bin/env python
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
import io, tempfile, codecs
import logging, logging.config

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
class TALContentTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		entry = """Some structure: <b tal:content="weblog/subject"></b>"""
		
		weblog = {'subject': 'Test subject', 'entry': entry}
		
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', 1)
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		self.context.addGlobal ('weblog', weblog)
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = io.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
			
	def testCompileTemplateBinary (self):
		""" Test creating an HTML template directly from a file that was binary opened.
			Write output to a binary file, letting simpleTAL do the encoding.
		"""
		# Create a temporary file, they auto-delete
		templateFile = tempfile.TemporaryFile (mode="w+b")
		# Write out the HTML in UTF-8
		txt = '<html><p>Somethings cost £3</p><p tal:content="one">Two</p></html>'
		expectedOutput = '<html><p>Somethings cost £3</p><p>1</p></html>'
		templateFile.write (txt.encode ('utf-8'))
		templateFile.seek (0)
		
		# Wrap the file in a reader, and bring it back in.
		reader = codecs.lookup ("utf-8").streamreader(templateFile)
		template = simpleTAL.compileHTMLTemplate (reader)
		
		# Now expand the template into a destination file that is binary
		outputFile = tempfile.TemporaryFile (mode="w+b")
		template.expand (self.context,outputFile)
		
		# Read it back in and compare with what we expected
		outputFile.seek(0)
		outputValue = outputFile.read ().decode ('utf-8')
		
		self.failUnless (outputValue == expectedOutput, "passed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (txt, outputValue, expectedOutput, template))
		
	def testCompileTemplateText (self):
		""" Test creating an HTML template directly from a file that was text opened.
			Write output to a text file, letting the caller do the encoding.
		"""
		# Create a temporary file manually
		try:
			fileHandle, fileName = tempfile.mkstemp ()
			with open (fileName, mode='t+w', encoding = "utf-8") as templateFile:
				# Write out the HTML in UTF-8
				txt = '<html><p>Somethings cost £3</p><p tal:content="one">Two</p></html>'
				expectedOutput = '<html><p>Somethings cost £3</p><p>1</p></html>'
				templateFile.write (txt)
				templateFile.seek (0)
			
				template = simpleTAL.compileHTMLTemplate (templateFile)
		finally:
			# Delete the temporary file we created
			os.remove (fileName)
		
		try:
			fileHandle, fileName = tempfile.mkstemp ()
			with open (fileName, mode="t+w", encoding = "utf-8") as outputFile:
				# Now expand the template into a destination file that is binary
				template.expand (self.context,outputFile)
				
				# Read it back in and compare with what we expected
				outputFile.seek(0)
				outputValue = outputFile.read ()
		finally:
			# Delete the temporary file we created
			os.remove (fileName)
			
		self.failUnless (outputValue == expectedOutput, "passed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (txt, outputValue, expectedOutput, template))
	

if __name__ == '__main__':
	unittest.main()

