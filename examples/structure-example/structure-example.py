import simpleTAL, simpleTALES

# Create the context that is used by the template
context = simpleTALES.Context()
context.addGlobal ("title", "Hello World")
context.addGlobal ("author", "Colin Stewart")

# A list that contains a dictionary
chapters = [{"heading": "Introduction", "text": "Some <b>text</b> here"}
					 ,{"heading": "Details", "text": "Notice tags are preserved."}
					 ,{"heading": "Advanced", "text": 'Structured text can contain TAL - written by <b tal:replace="author">Me</b>'}
					 ]
context.addGlobal ("doc", chapters)					 

templateFile = open ("structure.html", 'r')
result = simpleTAL.expandTemplate (templateFile, context)
templateFile.close()

print result