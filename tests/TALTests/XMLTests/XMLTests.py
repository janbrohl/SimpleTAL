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

import TALConditionTestCases,TALDefineTestCases,TALHandlerTestCases,TALContentTestCases,TALReplaceTestCases,TALRepeatTestCases,TALEncodingTestCases,TALForbiddenEndTagTestCases

def getAllTests ():
	allTestCases = unittest.TestSuite()
	for mod in [TALConditionTestCases
							,TALDefineTestCases
							,TALHandlerTestCases
							,TALContentTestCases
							,TALReplaceTestCases
							,TALRepeatTestCases
							,TALEncodingTestCases
							,TALForbiddenEndTagTestCases
				   ]:
		talesSuite = unittest.defaultTestLoader.loadTestsFromModule (mod)
		allTestCases.addTest (talesSuite)
	return allTestCases

if __name__ == '__main__':
	print "Running all XML tests."
	runner = unittest.TextTestRunner(verbosity='-v')
	runner.run(getAllTests())

