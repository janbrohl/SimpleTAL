#!/usr/bin/python
""" Example TAL program

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		An example of how to use METAL.
				
		Module Dependencies: simpleTAL, simpleTALES
"""

import simpleTAL, simpleTALES
import sys

# Creat the context that is used by the template
context = simpleTALES.Context()

# Add a string to the context under the variable title
context.addGlobal ("title", "Simple METAL Example")

# Compile the macro pages
templateFile = open ("macro.html", 'r')
macros = simpleTAL.compileHTMLTemplate (templateFile)
templateFile.close()

# Add the macros page to the Context
context.addGlobal ("sitemacros", macros)

# Now compile the page which will use the macros
templateFile = open ("page.html", 'r')
page = simpleTAL.compileHTMLTemplate (templateFile)
templateFile.close()

# Expand the page using this context
page.expand (context, sys.stdout)

