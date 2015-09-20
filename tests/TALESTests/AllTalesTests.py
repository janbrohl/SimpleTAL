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

import PathTests, ExistsTests, NoCallTests, NotTests, StringTests

print "Running all TALES tests."
runner = unittest.TextTestRunner(verbosity='-v')
for mod in [PathTests
		   ,ExistsTests
		   ,NoCallTests
		   ,NotTests
		   ,StringTests
		   ]:
	talesSuite = unittest.defaultTestLoader.loadTestsFromModule (mod)
	runner.run(talesSuite)
