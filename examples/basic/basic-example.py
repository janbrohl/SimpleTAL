#!/usr/bin/python
""" Example TAL program

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		As simple as it gets:
				1 - Create a context
				2 - Compile a template
				3 - Expand the template
		
		Module Dependencies: simpleTAL, simpleTALES
"""

from simpletal import simpleTAL, simpleTALES
import sys

# Creat the context that is used by the template
context = simpleTALES.Context()

# Add a string to the context under the variable title
context.addGlobal ("title", "Colours of the rainbow")

# A list of strings
colours = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
# Add the list to the context under the variable rainbow
context.addGlobal ("rainbow", colours)

# Open the template file
templateFile = open ("basic.html", 'r')

# Compile a template
template = simpleTAL.compileHTMLTemplate (templateFile)

# Close the template file
templateFile.close()

# Expand the template as HTML using this context
template.expand (context, sys.stdout)

