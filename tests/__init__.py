# -*- coding: iso-8859-1 -*-
from __future__ import unicode_literals
import unittest
import os.path


def discover():
    here = os.path.dirname(__file__)
    return unittest.defaultTestLoader.discover(here, "*Test*.py")


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(discover())
    return suite
