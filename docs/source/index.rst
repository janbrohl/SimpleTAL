.. SimpleTALSix documentation master file, created by
   sphinx-quickstart on Fri Apr 15 15:13:18 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for SimpleTALSix |version|
========================================

.. image:: https://codecov.io/github/janbrohl/SimpleTAL/coverage.svg?branch=six
    :target: https://codecov.io/github/janbrohl/SimpleTAL?branch=six
.. image:: https://travis-ci.org/janbrohl/SimpleTAL.svg?branch=six
    :target: https://travis-ci.org/janbrohl/SimpleTAL

This is an implementation of TAL_/METAL_ and TALES_ for Python 2.7 and 3.2+ (possibly working on other versions too)

SimpleTALSix is based on SimpleTAL_ 4.3.

Known limitations
-----------------

    * When using ``not:`` on an empty expression the result will be true rather than an error.
    * Path type ``python:`` is not supported by default. You can enable this by passing ``allowPythonPath=1`` to the Context constructor. Note that this should only be used when the authors of the templates are completely trusted, the code included in the ``python:`` path can do anything.
    * TAL markup ``on-error`` is not yet supported.
    * HTML Templates might have duplicate attributes if an attribute is added using ``tal:attributes`` and the name is in upper case. The cause of this is the HTMLParser implementation, which always converts attributes to lower case.


Contents
--------

.. toctree::
   :maxdepth: 2
   
   guide
   
   examples
   
   simpletal
   
   license
   


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _TAL: https://web.archive.org/web/20130517091955/http://wiki.zope.org/ZPT/TAL
.. _TALES: https://web.archive.org/web/20130517091955/http://wiki.zope.org/ZPT/TAL
.. _METAL: https://web.archive.org/web/20130517091955/http://wiki.zope.org/ZPT/TAL
.. _SimpleTAL: http://www.owlfish.com/software/simpleTAL/