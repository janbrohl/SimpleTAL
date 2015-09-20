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

import unittest, os, codecs, os.path, time
import StringIO
import logging, logging.config

from simpletal import simpleTALUtils, simpleTALES, simpleTAL

HTMLTemplate1 = """<html><body><h1 tal:content="title">Title</h1></body></html>"""
HTMLTemplate2 = """<html><body><h1 tal:content="title">Title</h1><p tal:content="message">Message</p></body></html>"""
XMLTemplate1 = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1 tal:content="title">Title</h1></body></html>"""
XMLTemplate2 = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1 tal:content="title">Title</h1><p tal:content="message">Message</p></body></html>"""
TEMP_DIR="/tmp/"
HTML_TEMPLATE_NAME='TemplateCacheTestCasesHtmlTemplate.html'
XML_TEMPLATE_NAME='TemplateCacheTestCasesXmlTemplate.xml'
EXPXML_TEMPLATE_NAME='TemplateCacheTestCasesXmlTemplate.xhtml'

#print "Macro is: %s" % str (macroTemplate)

class TemplateCacheTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.cache = simpleTALUtils.TemplateCache()
		
		self.context.addGlobal ('title', 'Cache Test')
		self.context.addGlobal ('message', 'Testing the cache...')
		
	def _runTest_ (self, template, txt, result, errMsg="Error"):
		realResult = simpleTALUtils.ExpandMacros (self.context, template)
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
			
	def testHTMLTemplateCacheNoFile (self):
		# Remove any previously created test files
		name = os.path.join (TEMP_DIR, HTML_TEMPLATE_NAME)
		try:
			os.remove (name)
		except:
			pass
		# This should error out...
		try:
			template = self.cache.getTemplate (name)
			self.fail ("Expected exception trying to retrieve anavailable template")
		except Exception, e:
			# Pass!
			pass
			
	def testHTMLTemplateCache (self):
		# Remove any previously created test files
		name = os.path.join (TEMP_DIR, HTML_TEMPLATE_NAME)
		try:
			os.remove (name)
		except:
			pass
		# Ensure that time ellapses so that a ctime change is recorded
		time.sleep (1)
		tf = open (name, 'w')
		tf.write (HTMLTemplate1)
		tf.close()
		
		# Get the template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<html><body><h1>Cache Test</h1></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 1, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<html><body><h1>Cache Test</h1></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.hits == 1, "Cache hit not recorded!")
		
		# Update the template, should cause a re-compile of the template
		# Ensure that time ellapses so that a ctime change is recorded
		time.sleep (1)
		tf = open (name, 'w')
		tf.write (HTMLTemplate2)
		tf.close()
		
		# Get the template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 2, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.hits == 2, "Cache hit not recorded!")
		
	def testXMLTemplateCacheNoFile (self):
		# Remove any previously created test files
		name = os.path.join (TEMP_DIR, XML_TEMPLATE_NAME)
		try:
			os.remove (name)
		except:
			pass
		# This should error out...
		try:
			template = self.cache.getTemplate (name)
			self.fail ("Expected exception trying to retrieve anavailable template")
		except Exception, e:
			# Pass!
			pass
			
	def testXMLTemplateCache (self):
		# Remove any previously created test files
		name = os.path.join (TEMP_DIR, XML_TEMPLATE_NAME)
		try:
			os.remove (name)
		except:
			pass
		# Ensure that time ellapses so that a ctime change is recorded
		time.sleep (1)
		tf = open (name, 'w')
		tf.write (XMLTemplate1)
		tf.close()
		
		# Get the template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 1, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.hits == 1, "Cache hit not recorded!")
		
		# Update the template, should cause a re-compile of the template
		# Ensure that time ellapses so that a ctime change is recorded
		time.sleep (1)
		tf = open (name, 'w')
		tf.write (XMLTemplate2)
		tf.close()
		
		# Get the template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 2, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.hits == 2, "Cache hit not recorded!")
		
	def testExplicitXMLTemplateCache (self):
		# Remove any previously created test files
		name = os.path.join (TEMP_DIR, EXPXML_TEMPLATE_NAME)
		try:
			os.remove (name)
		except:
			pass
		# Ensure that time ellapses so that a ctime change is recorded
		time.sleep (1)
		tf = open (name, 'w')
		tf.write (XMLTemplate1)
		tf.close()
		
		# Get the template
		template = self.cache.getXMLTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 1, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getXMLTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.hits == 1, "Cache hit not recorded!")
		
		# Update the template, should cause a re-compile of the template
		# Ensure that time ellapses so that a ctime change is recorded
		time.sleep (1)
		tf = open (name, 'w')
		tf.write (XMLTemplate2)
		tf.close()
		
		# Get the template
		template = self.cache.getXMLTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 2, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getXMLTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso-8859-1"?>\n<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.hits == 2, "Cache hit not recorded!")
		
if __name__ == '__main__':
	unittest.main()