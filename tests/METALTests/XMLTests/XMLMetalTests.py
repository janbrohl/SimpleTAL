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
import logging

import DefineMacroTests, DefineSlotsTests, METALNameSpaceTests

def getAllTests ():
	allTestCases = unittest.TestSuite()
	for mod in [DefineMacroTests
						 ,DefineSlotsTests
						 ,METALNameSpaceTests
					   ]:
		metalSuite = unittest.defaultTestLoader.loadTestsFromModule (mod)
		allTestCases.addTest (metalSuite)
	return allTestCases

if __name__ == '__main__':
	print "Running all METAL XML tests."
	runner = unittest.TextTestRunner(verbosity='-v')
	runner.run(getAllTests())

