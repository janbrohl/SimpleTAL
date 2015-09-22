import unittest

def load_tests(loader, tests, pattern):
	    here=__path__[0]
	    return unittest.defaultTestLoader.discover(here,"*Test*.py")
