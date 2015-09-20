""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Performance test cases.
		
"""
from simpletal import simpleTAL, simpleTALES

import time, StringIO, cStringIO, sys

performanceTemplate = """<html>
<head>
  <title></title>
      
  <meta http-equiv="content-type"
 content="text/html; charset=ISO-8859-1">
   
  <meta name="author" content="Colin Stewart">
</head>
<body>
 
<h1 tal:content="title">Performance Template</h1>
<div tal:repeat="things myList">
<h2 tal:content="string: $things/title itteration">Itteration title</h2>
<p tal:repeat="content things/content">
	<b tal:content="content/colour">Colour</b>
	<ul>
	  <li tal:repeat="anum content/num" tal:content="anum">All numbers</li>
	</ul>
</p>
</div>
 
</body>
</html>
"""

# 3 X 7 X 8 = 168 itterations per template expansion.
thirdLevelList = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]
secondLevelList = [{"colour": "red", "num": thirdLevelList}, {"colour": "orange", "num": thirdLevelList}, {"colour": "yellow", "num": thirdLevelList}, {"colour": "green", "num": thirdLevelList}, {"colour": "blue", "num": thirdLevelList}, {"colour": "indigo", "num": thirdLevelList}, {"colour": "violet", "num": thirdLevelList}]
firstLevelList = [{"title": "First", "content": secondLevelList}, {"title": "Second", "content": secondLevelList}, {"title": "Third", "content": secondLevelList}]

context = simpleTALES.Context()
context.addGlobal ("title", "Performance testing!")
context.addGlobal ("myList", firstLevelList )

def NGTemplates (count):
	tempFile = StringIO.StringIO (performanceTemplate)
	compiler = simpleTAL.HTMLTemplateCompiler()
	compiler.parseTemplate (tempFile)
	template = compiler.getTemplate()
	file = StringIO.StringIO ()
	start = time.clock()
	for attempt in xrange (count):
		template.expand (context, file)
	end = time.clock()
	#print "Resuling file: " + file.getvalue()
	return (end - start)
	
def NGTemplateOverhead (count):
	file = StringIO.StringIO ()
	start = time.clock()
	for attempt in xrange (count):
		tempFile = StringIO.StringIO (performanceTemplate)
		compiler = simpleTAL.HTMLTemplateCompiler()
		compiler.parseTemplate (tempFile)
		template = compiler.getTemplate()
		template.expand (context, file)
	end = time.clock()
	#print "Resuling file: " + file.getvalue()
	return (end - start)


print "Timing TAL templates"
result = NGTemplates (200)
print "Result: " + str(result) + " for 200 template expansions"

print "Timing TAL templates (with template parsing)"
result = NGTemplateOverhead (200)
print "Result: " + str(result) + " for 200 template expansions"

