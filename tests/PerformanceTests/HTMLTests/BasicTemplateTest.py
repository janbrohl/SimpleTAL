""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Performance test cases.
		
"""
import simpleTAL, simpleTALES

import time, StringIO, cStringIO, sys

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
 
<table cellpadding="2" cellspacing="2" border="1" width="100%">
   <tbody>
     <tr>
       <td valign="top">Simple<br>
       </td>
       <td valign="top">Sample<br>
       </td>
       <td valign="top">Real Results<br>
       </td>
       <td valign="top">Expected Results<br>
       </td>
     </tr>
     <tr>
       <td valign="top">Template parsed each time around the loop<br>
       </td>
       <td valign="top">100<br>
       </td>
       <td valign="top">Slow, SGMLParser takes a while<br>
       </td>
       <td valign="top">Slow<br>
       </td>
     </tr>
     <tr>
       <td valign="top">Template parsed once, then used multiple times<br>
       </td>
       <td valign="top">100<br>
       </td>
       <td valign="top">Fast!<br>
       </td>
       <td valign="top">Hopefully faster than parsing each time<br>
       </td>
     </tr>
     <tr>
       <td valign="top">XML Version<br>
       </td>
       <td valign="top">100<br>
       </td>
       <td valign="top">Faster than SGML<br>
       </td>
       <td valign="top">Still too slow<br>
       </td>
     </tr>
     <tr>
       <td valign="top">XML Version of TALTemplates<br>
       </td>
       <td valign="top">100<br>
       </td>
       <td valign="top">As fast as SGML<br>
       </td>
       <td valign="top">We can hope.<br>
       </td>
     </tr>
   
  </tbody> 
</table>
 Here's a list of thing:<br>
 
<ul tal:repeat="things myList">
   <li tal:content="things">An item</li>
</ul>
 That should do...<br>
 <br>
 
</body>
</html>
"""

context = simpleTALES.Context()
context.addGlobal ("title", "Performance testing!")
context.addGlobal ("myList", ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"])

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
result = NGTemplates (2000)
print "Result: " + str(result) + " for 2000 template expansions"

print "Timing TAL templates (with template parsing)"
result = NGTemplateOverhead (200)
print "Result: " + str(result) + " for 200 template expansions"

