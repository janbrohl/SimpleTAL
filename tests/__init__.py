# -*- coding: iso-8859-1 -*-
from __future__ import unicode_literals
import unittest


def get_loader():
    here = __path__[0]
    return unittest.defaultTestLoader.discover(here, "*Test*.py")


def load_tests(loader, tests, pattern):
    return loader()
