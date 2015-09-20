#!/usr/bin/env python

from distutils.core import setup

setup(name="SimpleTAL",
	version="3.3",
	description="SimpleTAL is a stand alone Python implementation of the TAL, TALES and METAL  specifications  used in Zope to power HTML and XML templates.",
	author="Colin Stewart",
	author_email="colin@owlfish.com",
	url="http://www.owlfish.com/software/simpleTAL/index.html",
	packages=[
		'simpletal',
	],
	package_dir = {'': 'lib'},
)
