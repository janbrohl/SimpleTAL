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

#import hotshot, hotshot.stats

import profile, pstats

import gc
print "Disabling garbage collection!"

gc.disable()

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
	file = simpleTALUtils.FastStringOutput()
	start = time.clock()
	for attempt in xrange (count):
		template.expand (context, file)
	end = time.clock()
	#print "Resuling file: " + file.getvalue()
	return (end - start)
	
def NGTemplateOverhead (count):
	file = file = simpleTALUtils.FastStringOutput()
	start = time.clock()
	for attempt in xrange (count):
		tempFile = StringIO.StringIO (performanceTemplate)
		compiler = simpleTAL.HTMLTemplateCompiler()
		compiler.parseTemplate (tempFile)
		template = compiler.getTemplate()
		#template.expand (context, file)
	end = time.clock()
	#print "Resuling file: " + file.getvalue()
	return (end - start)


print "Timing TAL templates"
#profiler = hotshot.Profile ("profile.data")
profiler = profile.run("NGTemplates (20)", "profile.data")
#profiler = profile.run("NGTemplateOverhead (20)", "profile.data")
#profiler.runcall (NGTemplates, 20)
print "Re-enabling garbage collection."
gc.enable()
print "Loading profile data."

#data = hotshot.stats.load ("profile.data")
data = pstats.Stats("profile.data")
data = data.strip_dirs()
sortedData = data.sort_stats ('time', 'calls')
sortedData.print_stats (25)
#sortedData.print_callees ('cmdRepeat')
#sortedData.print_callees ('cmdContent')
data.print_callees ('cmdEndTagEndScope')