#!/usr/bin/python
""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commerical and non-commerical use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""

import unittest, os
import StringIO
import logging

import TALConditionTestCases,TALDefineTestCases,TALHandlerTestCases,TALContentTestCases,TALReplaceTestCases,TALRepeatTestCases,TALEncodingTestCases

print "Running all XML tests."
runner = unittest.TextTestRunner(verbosity='-v')
for mod in [TALConditionTestCases
			,TALDefineTestCases
			,TALHandlerTestCases
			,TALContentTestCases
			,TALReplaceTestCases
			,TALRepeatTestCases
			,TALEncodingTestCases]:
	htmlSuite = unittest.defaultTestLoader.loadTestsFromModule (mod)
	runner.run(htmlSuite)
