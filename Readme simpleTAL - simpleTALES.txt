simpleTAL / simpleTALES (Version 1.1)
-------------------------------------
This is an implementation of the TAL and TALES specifications
see (http://www.zope.org/Documentation/Books/ZopeBook/current/AppendixC.stx)

This code is made freely available for commerical and non-commerical use. No
warranties, expressed or implied, are made as to the fitness of this code
for any purpose.

If this is of any use to anyone then please let me know, otherwise this 
may become the first and last release of this code.

The DummyLogger.py module is required if you do not have either Python 2.3
(un-tested on this) or the logging code from
http://www.red-dove.com/python_logging.html installed.  Just drop it, along
with simpleTAL.py and simpleTALES.py into your site-packages and all should
work.

Note that the unit test cases (under tests) require logging to be installed to run.

Known limitations
-----------------
Only a local namespace of 'tal' is supported.  You should be able to re-bind a different
name using XML namespaces, but this is not supported yet.  (i.e. you must always use the form
'tal:content' you can never use 'newName:content' with newName bound to the same namespace as
tal)

Repeat Variables do not support 'first' and 'last'.

When using 'not:' on an empty expression the result will be true rather than an error

Path type 'python:' is not supported.  I'm not keen on this path type because it allow
TAL Templates to do things other than pure presentment.  It should be easy to add if
required, although limiting the execution scope may be difficult.

on-error is not yet supported.

Known differences
-----------------

Non existant path types, e.g. '<b tal:content="total: $totalAmount"></b>' are not supported.  In
Zope this results in the path being interpreted as a string - in simpleTAL/ES the result will
be an error.

