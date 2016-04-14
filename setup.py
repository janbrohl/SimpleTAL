#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'lib'))

from setuptools import setup
import simpletal

setup(name="SimpleTALSix",
      version=simpletal.__version__,
      description="SimpleTAL is a stand alone Python implementation of the TAL, TALES and METAL  specifications  used in Zope to power HTML and XML templates.",
      author="Colin Stewart",
      author_email="colin@owlfish.com",
      maintainer="Jan Brohl",
      maintainer_email="janbrohl@t-online.de",
      url="https://github.com/janbrohl/SimpleTAL",
      provides=["SimpleTAL"],
      packages=[
          'simpletal'
      ],
      package_dir={'': 'lib'},
      tests_require="xmlcompare",
      test_suite='tests',
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
      ]
      )
