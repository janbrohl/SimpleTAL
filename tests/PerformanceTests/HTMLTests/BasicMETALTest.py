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
	file = simpleTALUtils.FastStringOutput()
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