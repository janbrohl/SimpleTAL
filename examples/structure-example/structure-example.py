""" Example TAL program

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		This shows how to include structure into a template, and how
		multiple templates can be embedded within each other.
		
		Module Dependencies: simpleTAL, simpleTALES
"""
import simpleTAL, simpleTALES
import sys

# Create the context that is used by the template
context = simpleTALES.Context()
context.addGlobal ("title", "Hello World")
context.addGlobal ("author", "Colin Stewart")

# A list that contains a dictionary
chapters = [{"heading": "Introduction", "text": "Some <b>text</b> here"}
					 ,{"heading": "Details", "text": "Notice tags are preserved."}
					 ]

advancedText = 'Structured text can contain other templates like this - written by <b tal:replace="author">Me</b>'

chapters.append ({"heading": "Advanced", "text": simpleTAL.compileHTMLTemplate (advancedText)})

context.addGlobal ("doc", chapters)

templateFile = open ("structure.html", 'r')
template = simpleTAL.compileHTMLTemplate (templateFile)

templateFile.close()

template.expand (context, sys.stdout)