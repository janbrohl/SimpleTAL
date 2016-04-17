#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
""" Example TAL program

		Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
		All rights reserved.
		
		Redistribution and use in source and binary forms, with or without
		modification, are permitted provided that the following conditions
		are met:
		1. Redistributions of source code must retain the above copyright
		   notice, this list of conditions and the following disclaimer.
		2. Redistributions in binary form must reproduce the above copyright
		   notice, this list of conditions and the following disclaimer in the
		   documentation and/or other materials provided with the distribution.
		3. The name of the author may not be used to endorse or promote products
		   derived from this software without specific prior written permission.
		
		THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
		IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
		OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
		IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
		INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
		NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
		DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
		THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
		THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		An example of how to use METAL.

"""
# Include to docs from here
from simpletal import simpleTAL, simpleTALES
import sys

# Creat the context that is used by the template
context = simpleTALES.Context()

# Add a string to the context under the variable title
context.addGlobal("title", "Simple METAL Example")

# Compile the macro pages
templateFile = open("macro.html", 'r')
macros = simpleTAL.compileHTMLTemplate(templateFile)
templateFile.close()

# Add the macros page to the Context
context.addGlobal("sitemacros", macros)

# Now compile the page which will use the macros
templateFile = open("page.html", 'r')
page = simpleTAL.compileHTMLTemplate(templateFile)
templateFile.close()

# Expand the page using this context
page.expand(context, sys.stdout)
