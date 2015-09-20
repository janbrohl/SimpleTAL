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

from simpletal import simpleTALUtils

isoText = """<html>
<h1>Some bad html follows</h1>
This is < than that, but > than this.

SimpleTAL & SimpleTALES = Simple Templating

This, though, is good: &pound;33!
(That's £33!)
</html>"""

uniText = unicode (isoText, "iso8859-1")

cleanResultText = """<html>
<h1>Some bad html follows</h1>
This is &lt; than that, but &gt; than this.

SimpleTAL &amp; SimpleTALES = Simple Templating

This, though, is good: &pound;33!
(That's £33!)
</html>"""

cleanResult = unicode (cleanResultText, "iso8859-1")

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
		result = cleaner.clean (isoText, "iso8859-1")
		self.failUnless (result == cleanResult, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (cleanResult, result))
		
	def testCleaningUniString (self):
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		result = cleaner.clean (uniText)
		self.failUnless (result == cleanResult, "Clean-up failed, expected:\n%s\n Got back:\n%s\n" % (cleanResult, result))

	def testCleaningISOStream (self):
		cleaner = simpleTALUtils.HTMLStructureCleaner ()
		isoStream = StringIO.StringIO (isoText)
		result = cleaner.clean (isoStream, "iso8859-1")
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