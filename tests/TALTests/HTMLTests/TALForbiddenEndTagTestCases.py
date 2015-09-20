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

import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
class TALForbiddenEndTagTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('link', 'www.owlfish.com')
		self.context.addGlobal ('scrWidth', '640')
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		template.expand (self.context, file)
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
						
	def testAreaElement (self):
		self._runTest_ ('<html><area tal:attributes="href link"></area></html>'
										,'<html><area href="www.owlfish.com"></html>'
										,"HTML Element AREA produced end tag.")

	def testBaseElement (self):
		self._runTest_ ('<html><base tal:attributes="href link"></base></html>'
										,'<html><base href="www.owlfish.com"></html>'
										,"HTML Element BASE produced end tag.")

	def testBaseFontElement (self):
		self._runTest_ ('<html><basefont tal:attributes="font test"></basefont></html>'
										,'<html><basefont font="testing"></html>'
										,"HTML Element BASEFONT produced end tag.")
										
	def testBRElement (self):
		self._runTest_ ('<html><br tal:attributes="class test"></br></html>'
										,'<html><br class="testing"></html>'
										,"HTML Element BR produced end tag.")

	def testColElement (self):
		self._runTest_ ('<html><col tal:attributes="width scrWidth"></col></html>'
										,'<html><col width="640"></html>'
										,"HTML Element COL produced end tag.")

	def testFrameElement (self):
		self._runTest_ ('<html><frame tal:attributes="href link"></frame></html>'
										,'<html><frame href="www.owlfish.com"></html>'
										,"HTML Element FRAME produced end tag.")
										
	def testHRElement (self):
		self._runTest_ ('<html><hr tal:attributes="class test"></hr></html>'
										,'<html><hr class="testing"></html>'
										,"HTML Element HR produced end tag.")
										
	def testImgElement (self):
		self._runTest_ ('<html><img tal:attributes="src link"></img></html>'
										,'<html><img src="www.owlfish.com"></html>'
										,"HTML Element IMG produced end tag.")
										
	def testInputElement (self):
		self._runTest_ ('<html><input tal:attributes="name test"></input></html>'
										,'<html><input name="testing"></html>'
										,"HTML Element INPUT produced end tag.")
										
	def testIsIndexElement (self):
		self._runTest_ ('<html><isindex tal:attributes="name test"></isindex></html>'
										,'<html><isindex name="testing"></html>'
										,"HTML Element ISINDEX produced end tag.")

	def testLinkElement (self):
		self._runTest_ ('<html><link tal:attributes="href link"></link></html>'
										,'<html><link href="www.owlfish.com"></html>'
										,"HTML Element LINK produced end tag.")

	def testMetaElement (self):
		self._runTest_ ('<html><meta tal:attributes="name test"></meta></html>'
										,'<html><meta name="testing"></html>'
										,"HTML Element META produced end tag.")

	def testParamElement (self):
		self._runTest_ ('<html><param tal:attributes="name test"></param></html>'
										,'<html><param name="testing"></html>'
										,"HTML Element PARAM produced end tag.")
										
	# Same tests again, but with no end tag in the templates
	def testAreaElementNoClose (self):
		self._runTest_ ('<html><area tal:attributes="href link"></html>'
										,'<html><area href="www.owlfish.com"></html>'
										,"HTML Element AREA produced end tag.")

	def testBaseElementNoClose (self):
		self._runTest_ ('<html><base tal:attributes="href link"></html>'
										,'<html><base href="www.owlfish.com"></html>'
										,"HTML Element BASE produced end tag.")

	def testBaseFontElementNoClose (self):
		self._runTest_ ('<html><basefont tal:attributes="font test"></html>'
										,'<html><basefont font="testing"></html>'
										,"HTML Element BASEFONT produced end tag.")
										
	def testBRElementNoClose (self):
		self._runTest_ ('<html><br tal:attributes="class test"></html>'
										,'<html><br class="testing"></html>'
										,"HTML Element BR produced end tag.")

	def testColElementNoClose (self):
		self._runTest_ ('<html><col tal:attributes="width scrWidth"></html>'
										,'<html><col width="640"></html>'
										,"HTML Element COL produced end tag.")

	def testFrameElementNoClose (self):
		self._runTest_ ('<html><frame tal:attributes="href link"></html>'
										,'<html><frame href="www.owlfish.com"></html>'
										,"HTML Element FRAME produced end tag.")
										
	def testHRElementNoClose (self):
		self._runTest_ ('<html><hr tal:attributes="class test"></html>'
										,'<html><hr class="testing"></html>'
										,"HTML Element HR produced end tag.")
										
	def testImgElementNoClose (self):
		self._runTest_ ('<html><img tal:attributes="src link"></html>'
										,'<html><img src="www.owlfish.com"></html>'
										,"HTML Element IMG produced end tag.")
										
	def testInputElementNoClose (self):
		self._runTest_ ('<html><input tal:attributes="name test"></html>'
										,'<html><input name="testing"></html>'
										,"HTML Element INPUT produced end tag.")
										
	def testIsIndexElementNoClose (self):
		self._runTest_ ('<html><isindex tal:attributes="name test"></html>'
										,'<html><isindex name="testing"></html>'
										,"HTML Element ISINDEX produced end tag.")

	def testLinkElementNoClose (self):
		self._runTest_ ('<html><link tal:attributes="href link"></html>'
										,'<html><link href="www.owlfish.com"></html>'
										,"HTML Element LINK produced end tag.")

	def testMetaElementNoClose (self):
		self._runTest_ ('<html><meta tal:attributes="name test"></html>'
										,'<html><meta name="testing"></html>'
										,"HTML Element META produced end tag.")

	def testParamElementNoClose (self):
		self._runTest_ ('<html><param tal:attributes="name test"></html>'
										,'<html><param name="testing"></html>'
										,"HTML Element PARAM produced end tag.")
										
if __name__ == '__main__':
	unittest.main()

