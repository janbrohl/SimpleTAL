#!/usr/bin/python
""" Example TAL based CGI

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		A demonstration of how TAL/TALES can be used from a cgi program.  Quick instructions:
			1 - Copy this file and the two templates ("fields.html" and "results.html") to 
			    the cgi-bin directory on your webserver
			2 - Ensure that simpleTAL, simpleTALES and DummyLogger are installed in your site-packages
			    directory
			3 - Go to http://servername/cgi-bin/simple-cgi.py
		
		Module Dependencies: simpleTAL, simpleTALES
"""

import simpleTAL, simpleTALES
import cgi, sys
		
class ExampleCGI:
	def __init__ (self):
		self.missingFields = {}
		self.fieldValues = {}
		self.form = cgi.FieldStorage()
		self.formValid = 1
		self.context = simpleTALES.Context()
		
	def buildContext (self, title):
		self.context.addGlobal ("missingFields", self.missingFields)
		self.context.addGlobal ("fieldValues", self.fieldValues)
		self.context.addGlobal ("title", title)
		
	def getValue (self, name, mandatory=1):
		if (self.form.has_key (name)):
			self.fieldValues [name] = self.form [name].value
		elif (mandatory):
			self.missingFields [name] = 1
			self.formValid = 0
			
	def main (self):
		if (self.form.has_key ("submit")):
			# Recieved the posting, get the name, occupation, and (optional) age
			self.getValue ("name")
			self.getValue ("occupation")
			self.getValue ("age", mandatory=0)
			
			if (self.formValid):
				# Valid form, show the results
				self.buildContext ("Valid Results")
				self.expandTemplate ("results.html")
			else:
				self.buildContext ("Missing fields")
				self.expandTemplate ("fields.html")
		else:
			self.buildContext ("Enter data")
			self.expandTemplate ("fields.html")

	def expandTemplate (self, templateName):
		# Print out the headers
		sys.stdout.write ("Content-Type: text/html\n")     # HTML is following
		sys.stdout.write ("\n")                            # blank line, end of headers
		
		# Expand the template and print it out
		templateFile = open (templateName, 'r')
		template = simpleTAL.compileHTMLTemplate (templateFile)

		# Close the template file
		templateFile.close()
		
		# Expand the template as HTML using this context
		template.expand (self.context, sys.stdout)

		sys.exit (0)				
			
# Entry point for the cgi
cgiInstance = ExampleCGI()
cgiInstance.main()
