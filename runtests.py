#!/usr/bin/env python

"""Regression testing framework

Borrowed from http://www.diveintopython.org/

This module will search for scripts in the same directory named
XYZtest.py.  Each such script should be a test suite that tests a
module through PyUnit.  (As of Python 2.1, PyUnit is included in
the standard library as "unittest".)  This script will aggregate all
found test suites into one big test suite and run them all at once.

* Modified to use os.path.walk to find all the test scripts
* Modified to find all python scripts, not just ones of the form *test.py
"""
import sys, os, re, unittest

# If logging is available, suppress it to avoid confusion.
try:
	import logging
	rootLogger = logging.getLogger ()
	rootLogger.setLevel (logging.CRITICAL)
except:
	pass

#ensure that the module in this directory is used instead of the system one
#or else we would be testing the system one and not the one with the changes :)
import sys
sys.path.insert(0, os.path.join(os.getcwd(),'lib'))
print "System path is: " + str (sys.path)
def path_vistor(files, dirname, names):
	"""Visits each file in the and appends the filename to the given list"""
	if (dirname.find ("PerformanceTests") > 0):
		return
	for name in names:
		files.append(os.path.join(dirname, name))

def regressionTest():
	#Find all the files to run
	files = []
	os.path.walk("tests", path_vistor, files)					
	test = re.compile(".*\.py$", re.IGNORECASE)
	files = filter(test.search, files)
	
	#load each test into the testsuite
	filenameToModuleName = lambda f: os.path.splitext(f)[0]
	moduleNames = map(filenameToModuleName, files)		 
	modules = map(__import__, moduleNames)				 
	load = unittest.defaultTestLoader.loadTestsFromModule
	return unittest.TestSuite(map(load, modules))

if __name__ == "__main__":
	unittest.main(defaultTest="regressionTest")
