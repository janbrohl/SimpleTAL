#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#    Copyright (c) 2016, Jan Brohl <janbrohl@t-online.de>
#    All rights reserved.
#    See LICENSE.txt

#    Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions
#    are met:
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. The name of the author may not be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
#    IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#    OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#    IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
#    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#    NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
#    THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#    If you make any bug fixes or feature enhancements please let me know!

""" 			
		Unit test cases.
		
"""

from __future__ import unicode_literals
import unittest
import os
import io
import logging
import logging.config

from simpletal import simpleTAL, simpleTALES

if (os.path.exists("logging.ini")):
    logging.config.fileConfig("logging.ini")
else:
    logging.basicConfig()

pageTemplate = simpleTAL.compileHTMLTemplate ("""<html>
<body metal:use-macro="site/macros/one">
<h1 metal:fill-slot="title">Expansion of macro one</h1>
</body>
</html>""")

pageTemplate2 = simpleTAL.compileHTMLTemplate ("""<html>
<body><div foo="a" tal:repeat="i string:abc">
<div metal:use-macro="site/macros/one"></div>
</div>
</body></html>""")


class DefineMacroTests (unittest.TestCase):

    def setUp(self):
        self.context = simpleTALES.Context()
        self.context.addGlobal('test', 'testing')
        self.context.addGlobal('link', 'www.owlfish.com')
        self.context.addGlobal ('needsQuoting', """Does "this" work?""")

    def _runTest_(self, txt, result, errMsg="Error"):
        macroTemplate = simpleTAL.compileHTMLTemplate(txt)
        self.context.addGlobal("site", macroTemplate)
        file = io.StringIO()
        pageTemplate.expand(self.context, file)
        realResult = file.getvalue()
