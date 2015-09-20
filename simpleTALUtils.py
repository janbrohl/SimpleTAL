""" simpleTALUtils

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commerical and non-commerical
		use.  No warranties, expressed or implied, are made as to the
		fitness of this code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		This module is holds utilities that make using SimpleTAL easier. 
		Initially this is just the HTMLStructureCleaner class, used to clean
		up HTML that can then be used as 'structure' content.
		
		Module Dependencies: None
"""

__version__ = "2.1"


import StringIO, os, sys, codecs, sgmllib, cgi

class HTMLStructureCleaner (sgmllib.SGMLParser):
	""" A helper class that takes HTML content and parses it, so converting
			any stray '&', '<', or '>' symbols into their respective entity references.
	"""
	def clean (self, content, encoding=None):
		""" Takes the HTML content given, parses it, and converts stray markup.
				The content can be either:
					 - A unicode string, in which case the encoding parameter is not required
					 - An ordinary string, in which case the encoding will be used
					 - A file-like object, in which case the encoding will be used if present
				
				The method returns a unicode string which is suitable for addition to a
				simpleTALES.Context object.
		"""
		if (type (content) == type ("")):
			# Not unicode, convert
			converter = codecs.lookup (encoding)[1]
			file = StringIO.StringIO (converter (content)[0])
		elif (type (content) == type (u"")):
			file = StringIO.StringIO (content)
		else:
			# Treat it as a file type object - and convert it if we have an encoding
			if (encoding is not None):
				converterStream = codecs.lookup (encoding)[2]
				file = converterStream (content)
			else:
				file = content
		
		self.outputFile = StringIO.StringIO (u"")
		self.feed (file.read())
		self.close()
		return self.outputFile.getvalue()
		
	def unknown_starttag (self, tag, attributes):
		self.outputFile.write (tagAsText (tag, attributes))
		
	def unknown_endtag (self, tag):
		self.outputFile.write ('</' + tag + '>')
			
	def handle_data (self, data):
		self.outputFile.write (cgi.escape (data))
		
	def handle_charref (self, ref):
		self.outputFile.write (u'&#%s;' % ref)
		
	def handle_entityref (self, ref):
		self.outputFile.write (u'&%s;' % ref)
			

def tagAsText (tag,atts):
	result = "<" + tag 
	for att in atts:
		result += ' ' + att[0] + '="' + att[1] + '"'
	result += ">"
	return result

