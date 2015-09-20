""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Performance test cases.
		
"""
from simpletal import simpleTAL, simpleTALES, simpleTALUtils

import time, StringIO, cStringIO, sys

macroTemplate = """<html>
<body>
<h1>Macros follow</h1>
<div metal:define-macro="one">
<h2>A sample macro</h2>
<ul>
  <li><b metal:define-slot="first">First</b></li>
</ul>
</div>

<div metal:define-macro="two">
<table>
  <tr>
    <th>Important Stuff, worth £££s</th>
  </tr>
  <tr>
    <td><b metal:define-slot="tableEntry">Table</b></td>
  </tr>
</table>
</div>
</body>
</html>
"""

performanceTemplate = """<html>
<head>
  <title></title>
      
  <meta http-equiv="content-type"
 content="text/html; charset=ISO-8859-1">
   
  <meta name="author" content="Colin Stewart">
</head>
<body>
 
<h1>Performance Template</h1>
 Some text, with some <b>tags <i>that</i> are</b> adding to the parsing load.<br>
 
<h2 tal:content="title">This title is dynamic</h2>
 Here's a table as well - lots of tags in there:<br>
 
Here's a list of thing:<br>
 
<div tal:repeat="things myList" tal:omit-tag="">
   <p metal:use-macro="macTemp/macros/one">
     <i metal:fill-slot="first" tal:content="things">things</i>
   </p>
   
   <p metal:use-macro="macTemp/macros/two" tal:omit-tag="">
     <i metal:fill-slot="tableEntry" tal:content="things">things</i>
   </p>
</div>
That should do...<br>
 <br>
 
</body>
</html>
"""

context = simpleTALES.Context()
context.addGlobal ("title", "Performance testing!")
context.addGlobal ("myList", ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"])
template = simpleTAL.compileHTMLTemplate (performanceTemplate)
macTemplate = simpleTAL.compileHTMLTemplate (macroTemplate)
context.addGlobal ("macTemp", macTemplate)

def METALTime (count, template):
	file = StringIO.StringIO ()
	start = time.clock()
	for attempt in xrange (count):
		template.expand (context, file)
	end = time.clock()
	#print "Resuling file: " + file.getvalue()
	return (end - start)

#print "Timing TAL templates"
#result = NGTemplates (2000)
#print "Result: " + str(result) + " for 2000 template expansions"

# Pre-expand macros
expanded = simpleTALUtils.ExpandMacros (context, template)
#print expanded
realTemplate = simpleTAL.compileHTMLTemplate (expanded)

print "Timing macro expansion..."
result = METALTime (400, realTemplate)
print "Total time %s for 400 itterations" % (str (result))