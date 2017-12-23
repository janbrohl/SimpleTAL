#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'lib'))

from setuptools import setup
import simpletal

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="SimpleTALSix",
    version=simpletal.__version__,
    description=
    "Stand alone Python implementation of the TAL, TALES and METAL specifications used in Zope to power HTML and XML templates.",
    long_description=long_description,
    author="Colin Stewart",
    author_email="colin@owlfish.com",
    maintainer="Jan Brohl",
    maintainer_email="janbrohl@t-online.de",
    url="https://github.com/janbrohl/SimpleTAL",
    provides=["SimpleTAL"],
    packages=['simpletal'],
    python_requires="~=2.7,~=3.2",
    package_dir={'': 'lib'},
    tests_require="xmlcompare",
    test_suite='tests',
    license="BSD-3-Clause",
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ])
