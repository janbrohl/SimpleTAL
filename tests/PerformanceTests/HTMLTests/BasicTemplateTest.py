"""		Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
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
		
		Performance test cases.
		
"""
from simpletal import simpleTAL, simpleTALES, simpleTALUtils

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
	file = simpleTALUtils.FastStringOutput()
	start = time.clock()
	for attempt in xrange (count):
		template.expand (context, file)
	end = time.clock()
	#print "Resuling file: " + file.getvalue()
	return (end - start)
	
def NGTemplateOverhead (count):
	file = simpleTALUtils.FastStringOutput()
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

