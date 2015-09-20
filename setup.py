#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.join(os.getcwd(),'lib'))

from distutils.core import setup
import simpletal

setup(name="SimpleTAL",
	version= simpletal.__version__,
	description="SimpleTAL is a stand alone Python implementation of the TAL, TALES and METAL  specifications  used in Zope to power HTML and XML templates.",
	author="Colin Stewart",
	author_email="colin@owlfish.com",
	url="http://www.owlfish.com/software/simpleTAL/index.html",
	packages=[
		'simpletal',
	],
	package_dir = {'': 'lib'},
)
