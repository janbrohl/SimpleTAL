#!/usr/bin/python
"""		Copyright (c) 2005 Colin Stewart (http://www.owlfish.com/)
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

import unittest, os, sys
import StringIO
import logging, logging.config

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
try:
	b = StopIteration()
	ITERATOR_SUPPORT = 1
except:
	ITERATOR_SUPPORT = 0
	
class ActualIter:
	def __init__ (self, size):
		self.size = size
		self.cur = 0
		
	def next (self):
		if (self.cur == self.size):
			raise StopIteration ()
		self.cur += 1
		return self.cur
	
class IterContainer:
	def __init__ (self, size):
		self.size = size
		
	def __iter__ (self):
		return ActualIter (self.size)
	
class TALIteratorRepeatTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('zeroCont', IterContainer (0))
		self.context.addGlobal ('oneCont', IterContainer (1))
		self.context.addGlobal ('twoCont', IterContainer (2))
		
		self.context.addGlobal ('zeroAct', ActualIter (0))
		self.context.addGlobal ('oneAct', ActualIter (1))
		self.context.addGlobal ('twoAct', ActualIter (2))
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		if (not ITERATOR_SUPPORT):
			return
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		try:
			template.expand (self.context, file)
		except Exception, e:
			print "Error, template compiled to: " + str (template)
			raise e
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
					
	def testZeroCont (self):
		self._runTest_ ('<html><p tal:repeat="entry zeroCont">Hello</p></html>', "<html></html>", "Repeat of zero length container failed.")
		
	def testOneCont (self):
		self._runTest_ ('<html><p tal:repeat="entry oneCont">Hello</p></html>', "<html><p>Hello</p></html>", "Repeat of single length container failed.")
	
	def testTwoCont (self):
		self._runTest_ ('<html><p tal:repeat="entry twoCont">Hello</p></html>', "<html><p>Hello</p><p>Hello</p></html>", "Repeat of two length container failed.")
		
	def testZeroAct (self):
		self._runTest_ ('<html><p tal:repeat="entry zeroAct">Hello</p></html>', "<html></html>", "Repeat of zero length actual failed.")
		
	def testOneAct (self):
		self._runTest_ ('<html><p tal:repeat="entry oneAct">Hello</p></html>', "<html><p>Hello</p></html>", "Repeat of single length actual failed.")
	
	def testTwoAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct">Hello</p></html>', "<html><p>Hello</p><p>Hello</p></html>", "Repeat of two length actual failed.")
	
	def testIndexAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/index">Hello</p></html>', "<html><p>0</p><p>1</p></html>", "Repeat of two length actual iterator failed to generate index.")
		
	def testNumberAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/number">Hello</p></html>', "<html><p>1</p><p>2</p></html>", "Repeat of two length actual iterator failed to generate numbers.")
		
	def testEvenAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/even">Hello</p></html>', "<html><p>1</p><p>0</p></html>", "Repeat of two length actual iterator failed to even.")
	
	def testOddAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/odd">Hello</p></html>', "<html><p>0</p><p>1</p></html>", "Repeat of two length actual iterator failed to odd.")
	
	def testStartAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/start">Hello</p></html>', "<html><p>1</p><p>0</p></html>", "Repeat of two length actual iterator failed to start.")

# The only way to see inside an iterator is to cheat, and call it early.  Doing this might be unexpected, so iterators don't support end.
#	def testEndAct (self):
#		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/end">Hello</p></html>', "<html><p>0</p><p>1</p></html>", "Repeat of two length actual iterator failed to end.")

	def testLengthAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/length">Hello</p></html>', "<html><p>%s</p><p>%s</p></html>" % (str (sys.maxint), str (sys.maxint)), "Repeat of two length actual iterator failed to generate length.")

	def testLetterSmallAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/letter">Hello</p></html>', "<html><p>a</p><p>b</p></html>", "Repeat of two length actual iterator failed to letter.")
	
	def testLetterAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/Letter">Hello</p></html>', "<html><p>A</p><p>B</p></html>", "Repeat of two length actual iterator failed to Letter.")
		
	def testSmallRomanNumAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/roman">Hello</p></html>', "<html><p>i</p><p>ii</p></html>", "Repeat of two length actual iterator failed to generate roman numerals.")
	
	def testRomanNumAct (self):
		self._runTest_ ('<html><p tal:repeat="entry twoAct" tal:content="repeat/entry/Roman">Hello</p></html>', "<html><p>I</p><p>II</p></html>", "Repeat of two length actual iterator failed to generate roman numerals.")
		