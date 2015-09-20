simpleTAL / simpleTALES (Version 3.13)
-------------------------------------
This is an implementation of the TAL and TALES specifications
see (http://www.zope.org/Documentation/Books/ZopeBook/current/AppendixC.stx)

Installation
------------
To install SimpleTAL under Unix:
  
  (Note that to perform the installation of SimpleTAL you will probably
   have to have the Python Development package installed.)
  
  1 - Become root
  2 - Run "python setup.py install"
	
Under MacOS X:
  1 - Run "sudo python setup.py install"
  2 - Close the terminal program and re-open it.
  
Notes
-----
This code is made freely available under a BSD style license, see 
LICENSE.txt for more details.

The DummyLogger.py module is used if you do not have either Python 2.3 
or the logging code from
http://www.red-dove.com/python_logging.html installed.

Note that the unit test cases (under tests) require logging to be installed
to run.

Documentation
-------------
Documentation on the SimpleTAL API can be found in documentation/html/
