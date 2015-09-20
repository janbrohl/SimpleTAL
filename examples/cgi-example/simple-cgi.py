#!/usr/bin/python
""" Example TAL based CGI

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
		
		A demonstration of how TAL/TALES can be used from a cgi program.  Quick instructions:
			1 - Copy this file and the two templates ("fields.html" and "results.html") to 
			    the cgi-bin directory on your webserver
			2 - Ensure that simpleTAL, simpleTALES and DummyLogger are installed in your site-packages
			    directory
			3 - Go to http://servername/cgi-bin/simple-cgi.py
		
		Module Dependencies: simpleTAL, simpleTALES
"""

from simpletal import simpleTAL, simpleTALES
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
			self.getValue ("username")
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
