#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'lib'))

from distutils.core import setup
import simpletal

setup(name="SimpleTAL",
      version=simpletal.__version__,
      description="SimpleTAL is a stand alone Python implementation of the TAL, TALES and METAL  specifications  used in Zope to power HTML and XML templates.",
      author="Colin Stewart",
      author_email="colin@owlfish.com",
      url="http://www.owlfish.com/software/simpleTAL/index.html",
      packages=[
          'simpletal'
      ],
      package_dir={'': 'lib'},
      classifiers=[
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
      ]
      )
