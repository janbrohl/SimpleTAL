#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
""" 	Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
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

import unittest, os, codecs
import StringIO
import logging, logging.config

from simpletal import simpleTALUtils

isoText = """<html>
<h1>Some bad html follows</h1>
This is < than that, but > than this.

SimpleTAL & SimpleTALES = Simple Templating

This, though, is good: &pound;33!
(That's £33!)
</html>"""

uniText = unicode (isoText, "iso-8859-1")

cleanResultText = """<html>
<h1>Some bad html follows</h1>
This is &lt; than that, but &gt; than this.

SimpleTAL &amp; SimpleTALES = Simple Templating

This, though, is good: &pound;33!
(That's £33!)
</html>"""

cleanResult = unicode (cleanResultText, "iso-8859-1")

class HTMLStructureCleanerTestCases (unittest.TestCase):
	def setUp (self):
		pass
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testCleaningISOString (self):
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		result = cleaner.clean (isoText, "iso-8859-1")
		self.failUnless (result == cleanResult, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (cleanResult, result))
		
	def testCleaningUniString (self):
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		result = cleaner.clean (uniText)
		self.failUnless (result == cleanResult, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (cleanResult, result))

	def testCleaningISOStream (self):
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		isoStream = StringIO.StringIO (isoText)
		result = cleaner.clean (isoStream, "iso-8859-1")
		self.failUnless (result == cleanResult, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (cleanResult, result))

	def testCleaningUniStream (self):
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		uniStream = StringIO.StringIO (uniText)
		result = cleaner.clean (uniStream)
		self.failUnless (result == cleanResult, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (cleanResult, result))
				
	def testCleanURL (self):
		goodLink = u"""<html><a href="http://news.ft.com/servlet/ContentServer?pagename=FT.com/StoryFT/FullStory&amp;c=StoryFT&amp;cid=1042491488445&amp;p=1012571727088">link</a></html>"""
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		uniStream = StringIO.StringIO (goodLink)
		result = cleaner.clean (uniStream)
		self.failUnless (result == goodLink, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (goodLink.encode ('ascii', 'ignore'), result.encode ('ascii', 'ignore')))		

	def testUnCleanURL (self):
		badLink = u"""<html><a href="http://news.ft.com/servlet/ContentServer?pagename=FT.com/StoryFT/FullStory&c=StoryFT&cid=1042491488445&p=1012571727088">link</a></html>"""
		goodLink = u"""<html><a href="http://news.ft.com/servlet/ContentServer?pagename=FT.com/StoryFT/FullStory&amp;c=StoryFT&amp;cid=1042491488445&amp;p=1012571727088">link</a></html>"""
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		uniStream = StringIO.StringIO (badLink)
		result = cleaner.clean (uniStream)
		self.failUnless (result == goodLink, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (goodLink.encode ('ascii', 'ignore'), result.encode ('ascii', 'ignore')))		
		
if __name__ == '__main__':
	unittest.main()