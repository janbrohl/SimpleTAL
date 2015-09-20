#!/usr/bin/python
""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""

import unittest, os, codecs, os.path, time
import StringIO
import logging, logging.config

from simpletal import simpleTALUtils, simpleTALES, simpleTAL

HTMLTemplate1 = """<html><body><h1 tal:content="title">Title</h1></body></html>"""
HTMLTemplate2 = """<html><body><h1 tal:content="title">Title</h1><p tal:content="message">Message</p></body></html>"""
XMLTemplate1 = """<?xml version="1.0" encoding="iso8859-1"?>\n<html><body><h1 tal:content="title">Title</h1></body></html>"""
XMLTemplate2 = """<?xml version="1.0" encoding="iso8859-1"?>\n<html><body><h1 tal:content="title">Title</h1><p tal:content="message">Message</p></body></html>"""
TEMP_DIR="/tmp/"
HTML_TEMPLATE_NAME='TemplateCacheTestCasesHtmlTemplate.html'
XML_TEMPLATE_NAME='TemplateCacheTestCasesXmlTemplate.xml'

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
		expectedResult = """<?xml version="1.0" encoding="iso8859-1"?>\n<html><body><h1>Cache Test</h1></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 1, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso8859-1"?>\n<html><body><h1>Cache Test</h1></body></html>"""
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
		expectedResult = """<?xml version="1.0" encoding="iso8859-1"?>\n<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.misses == 2, "Cache miss not recorded!")
		# Get the cached template
		template = self.cache.getTemplate (name)
		outputFile = StringIO.StringIO ()
		template.expand (self.context, outputFile)
		expectedResult = """<?xml version="1.0" encoding="iso8859-1"?>\n<html><body><h1>Cache Test</h1><p>Testing the cache...</p></body></html>"""
		self.failUnless (outputFile.getvalue() == expectedResult
										,"Error: template did not expand to expected result.  Expected: %s got: %s" % (expectedResult, outputFile.getvalue()))
		self.failUnless (self.cache.hits == 2, "Cache hit not recorded!")
		
if __name__ == '__main__':
	unittest.main()