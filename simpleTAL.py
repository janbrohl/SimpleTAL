""" simpleTAL Interpreter

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commerical and non-commerical
		use.  No warranties, expressed or implied, are made as to the
		fitness of this code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		
		The classes in this module implement the TAL language, expanding
		both XML and HTML templates.
		
		Module Dependencies: logging, simpleTALES, simpleTALTemplates
"""

__version__ = "2.1"

try:
	import logging
except:
	import DummyLogger as logging
	
import sgmllib, xml.sax, cgi, string, StringIO, codecs

import simpleTALES
	
# All commands are of the form (opcode, args, commandList)
# The numbers are the opcodes, and also the order of priority

# Argument: [(isLocalFlag (Y/n), variableName, variablePath),...]
TAL_DEFINE = 1
# Argument: expression, endTagSymbol
TAL_CONDITION = 2
# Argument: (varname, expression, endTagSymbol)
TAL_REPEAT = 3
# Argument: (replaceFlag, type, expression)
TAL_CONTENT = 4
# Not used in byte code, only ordering.
TAL_REPLACE = 5
# Argument: [(attributeName, expression)]
TAL_ATTRIBUTES = 6
# Argument: expression
TAL_OMITTAG = 7
# Argument: (originalAttributeList, currentAttributeList)
TAL_START_SCOPE = 8
# Argument: String to output
TAL_OUTPUT = 9
# Argument: None
TAL_STARTTAG = 10
# Argument: Tag, omitTagFlag
TAL_ENDTAG_ENDSCOPE = 11
# Argument: None
TAL_NOOP = 13

TAL_ATTRIBUTE_MAP = {'tal:attributes': TAL_ATTRIBUTES, 'tal:content': TAL_CONTENT
									  ,'tal:define': TAL_DEFINE, 'tal:replace': TAL_REPLACE
									  ,'tal:omit-tag': TAL_OMITTAG, 'tal:condition': TAL_CONDITION
									  ,'tal:repeat': TAL_REPEAT}
									  
class Template:
	def __init__ (self, commands, symbols):
		self.commandList = commands
		self.symbolTable = symbols
		self.commandHandler  = {}
		self.commandHandler [TAL_DEFINE] = self.cmdDefine;
		self.commandHandler [TAL_CONDITION] = self.cmdCondition;
		self.commandHandler [TAL_REPEAT] = self.cmdRepeat;
		self.commandHandler [TAL_CONTENT] = self.cmdContent;
		self.commandHandler [TAL_ATTRIBUTES] = self.cmdAttributes;
		self.commandHandler [TAL_OMITTAG] = self.cmdOmitTag;
		self.commandHandler [TAL_START_SCOPE] = self.cmdStartScope
		self.commandHandler [TAL_OUTPUT] = self.cmdOutput;		
		self.commandHandler [TAL_STARTTAG] = self.cmdOutputStartTag
		self.commandHandler [TAL_ENDTAG_ENDSCOPE] = self.cmdEndTagEndScope
		self.commandHandler [TAL_NOOP] = self.cmdNoOp;
		
	def cleanState (self):
		self.scopeStack = []
		self.programCounter = 0
		self.movePCForward = None
		self.movePCBack = None
		self.outputTag = 1
		self.originalAttributes = []
		self.currentAttributes = []
		self.repeatVariable = None
		self.repeatIndex = 0
		self.repeatSequence = None
		self.tagContent = None
		# tagState flag as to whether there are any local variables to pop
		self.localVarsDefined = 0

	def expand (self, context, outputFile, outputEncoding=None):
		""" This method will write to the outputFile, using the encoding specified,
				the expanded version of this template.  The context passed in is used to resolve
				all expressions with the template.
		"""
		# This method must wrap outputFile if required by the encoding, and write out
		# any template pre-amble (DTD, Encoding, etc)
		self.expandInline (context, outputFile)
		
	def expandInline (self, context, outputFile):
		""" Internally used when expanding a template that is part of a context."""
		self.context = context
		self.file = outputFile
		self.cleanState()
		self.execute (self.commandList)
		self.context = None
		self.file = None
		self.programCounter = 0
		
	def execute (self, cmndList):
		programLength = len (cmndList)
		while (self.programCounter < programLength):
			cmnd = cmndList [self.programCounter]
			#print "Executing command: " + str (cmnd)
			self.commandHandler[cmnd[0]] (cmnd[0], cmnd[1])
		
	def cmdDefine (self, command, args):
		""" args: [(isLocalFlag (Y/n), variableName, variablePath),...]
				Define variables in either the local or global context
		"""
		localVarList = []
		for isLocal, varName, varPath in args:
			result = self.context.evaluate (varPath, self.originalAttributes)
			if (isLocal):
				localVarList.append ((varName, result.value()))
			else:
				self.context.addGlobal (varName, result.value())
		if (len (localVarList) > 0):
			self.localVarsDefined = 1
			self.context.addLocals (localVarList)
		self.programCounter += 1
		
	def cmdCondition (self, command, args):
		""" args: expression, endTagSymbol
				Conditionally continues with execution of all content contained
				by it.
		"""
		result = self.context.evaluate (args[0], self.originalAttributes)
		if (result is None or not result.isTrue()):
			# Nothing to output - evaluated to false.
			self.outputTag = 0
			self.programCounter = self.symbolTable[args[1]]
			return
		self.programCounter += 1
		
	def cmdRepeat (self, command, args):
		""" args: (varName, expression, endTagSymbol)
				Repeats anything in the cmndList
		"""		
		if (self.repeatVariable is not None):
			# We are already part way through a repeat
			self.repeatIndex += 1
			if (self.repeatIndex == len (self.repeatSequence)):
				# We have finished the repeat
				self.repeatVariable = None
				self.context.removeRepeat (args[0])
				self.context.popLocals()
				self.movePCBack = None
				# Suppress the final close tag
				self.outputTag = 0
				self.programCounter = self.symbolTable [args[2]]
				return
			self.context.setLocal (args[0], self.repeatSequence[self.repeatIndex])
			self.repeatVariable.increment()
			self.programCounter += 1
			return
		
		# The first time through this command
		result = self.context.evaluate (args[1], self.originalAttributes)
		if (result is not None and result.isDefault()):
			# Leave everything un-touched.
			self.programCounter += 1
			return
		if (result is None or result.isNothing() or not result.isSequence()):
			# Delete the tags and their contents
			self.outputTag = 0
			self.programCounter = self.symbolTable [args[2]]
			return
		
		# We really do want to repeat - so lets do it
		self.repeatSequence = result.value()
		self.movePCBack = self.programCounter
		self.repeatVariable = simpleTALES.RepeatVariable (self.repeatSequence)
		self.context.addRepeat (args[0], self.repeatVariable)
		self.context.addLocals ([(args[0], self.repeatSequence[self.repeatIndex])])
		self.programCounter += 1
	
	def cmdContent (self, command, args):
		""" args: (replaceFlag, structureFlag, expression, endTagSymbol)
				Expands content
		"""		
		result = self.context.evaluate (args[2], self.originalAttributes)
		if (result is None or result.isNothing()):
			if (args[0]):
				# Only output tags if this is a content not a replace
				self.outputTag = 0
			# Output none of our content or the existing content, but potentially the tags
			self.movePCForward = self.symbolTable [args[3]]
			self.programCounter += 1
			return
		elif (not result.isDefault()):
			# We have content, so let's suppress the natural content and output this!
			if (args[0]):
				self.outputTag = 0
			self.tagContent = (args[1], result.value())
			self.movePCForward = self.symbolTable [args[3]]
			self.programCounter += 1
			return
		else:
			# Default, let's just run through as normal
			self.programCounter += 1
			return
		
	def cmdAttributes (self, command, args):
		""" args: [(attributeName, expression)]
				Add, leave, or remove attributes from the start tag
		"""
		attsToRemove = {}
		newAtts = []
		for attName, attExpr in args:
			result = self.context.evaluate (attExpr, self.originalAttributes)
			if (result is None or result.isNothing()):
				# Remove this attribute from the current attributes
				attsToRemove [attName]=1
			elif (not result.isDefault()):
				# We have a value - let's use it!
				attsToRemove [attName]=1
				escapedAttVal = (cgi.escape (result.value())).replace ('"', '&quot;')
				newAtts.append ((attName,escapedAttVal))
		# Copy over the old attributes 
		for oldAtt in self.currentAttributes:
			if (not attsToRemove.has_key (oldAtt[0])):
				newAtts.append (oldAtt)
		self.currentAttributes = newAtts
		# Evaluate all other commands
		self.programCounter += 1
		
	def cmdOmitTag (self, command, args):
		""" args: expression
				Conditionally turn off tag output
		"""
		result = self.context.evaluate (args, self.originalAttributes)
		if (result is not None and result.isTrue()):
			# Turn tag output off
			self.outputTag = 0
		self.programCounter += 1
		
	def cmdOutputStartTag (self, command, args):
		# Args: tagName
		if (self.outputTag):
			self.file.write (tagAsText ((args, self.currentAttributes)))
		
		if (self.tagContent is not None):
			contentType, resultVal = self.tagContent
			if (contentType):
				if (isinstance (resultVal, Template)):
					# We have another template in the context, evaluate it!
					resultVal.expandInline (self.context, self.file)
				else:
					if (type (resultVal) == type (u"")):
						self.file.write (resultVal)
					elif (type (resultVal) == type ("")):
						self.file.write (unicode (resultVal, 'ascii'))
					else:
						self.file.write (unicode (str (resultVal), 'ascii'))
			else:
				if (type (resultVal) == type (u"")):
					self.file.write (cgi.escape (resultVal))
				elif (type (resultVal) == type ("")):
					self.file.write (cgi.escape (unicode (resultVal, 'ascii')))
				else:
					self.file.write (cgi.escape (unicode (str (resultVal), 'ascii')))
				
		if (self.movePCForward is not None):
			self.programCounter = self.movePCForward
			return
		self.programCounter += 1
		return
	
	def cmdEndTagEndScope (self, command, args):
		# Args: tagName, omitFalg
		if (self.outputTag and not args[1]):
			self.file.write ('</' + args[0] + '>')
		
		if (self.movePCBack is not None):
			self.programCounter = self.movePCBack
			return
			
		if (self.localVarsDefined):
			self.context.popLocals()
			
		self.movePCForward,self.movePCBack,self.outputTag,self.originalAttributes,self.currentAttributes,self.repeatVariable,self.repeatIndex,self.repeatSequence,self.tagContent,self.localVarsDefined = self.scopeStack.pop()			
		self.programCounter += 1
	
	def cmdOutput (self, command, args):
		self.file.write (args)
		self.programCounter += 1
		
	def cmdStartScope (self, command, args):
		""" args: (originalAttributes, currentAttributes)
				Pushes the current state onto the stack, and sets up the new state
		"""
		self.scopeStack.append ((self.movePCForward
														,self.movePCBack
														,self.outputTag
														,self.originalAttributes
														,self.currentAttributes
														,self.repeatVariable
														,self.repeatIndex
														,self.repeatSequence
														,self.tagContent
														,self.localVarsDefined))

		self.movePCForward = None
		self.movePCBack = None
		self.outputTag = 1
		self.originalAttributes = args[0]
		self.currentAttributes = args[1]
		self.repeatVariable = None
		self.repeatIndex = 0
		self.repeatSequence = None
		self.tagContent = None
		self.localVarsDefined = 0
		
		self.programCounter += 1				
				
	def cmdNoOp (self, command, args):
		self.programCounter += 1
		
	def __str__ (self):
		result = "Commands:\n"
		for cmd in self.commandList:
			result = result + "\n" + str (cmd)
		result = result + "\n\nSymbols:\n"
		for symbol in self.symbolTable.keys():
			result = result + "Symbol: " + str (symbol) + " points to: " + str (self.symbolTable[symbol]) + ", which is command: " + str (self.commandList[self.symbolTable[symbol]]) + "\n"
		return result
		
class HTMLTemplate (Template):
	"""A specialised form of a template that knows how to output HTML
	"""
	
	def expand (self, context, outputFile, outputEncoding="ISO-8859-1"):
		""" This method will write to the outputFile, using the encoding specified,
				the expanded version of this template.  The context passed in is used to resolve
				all expressions with the template.
		"""
		# This method must wrap outputFile if required by the encoding, and write out
		# any template pre-amble (DTD, Encoding, etc)
		
		encodingFile = codecs.lookup (outputEncoding)[3](outputFile)
		self.expandInline (context, encodingFile)
		
class XMLTemplate (Template):
	"""A specialised form of a template that knows how to output XML
	"""
	
	def expand (self, context, outputFile, outputEncoding="iso8859-1"):
		""" This method will write to the outputFile, using the encoding specified,
				the expanded version of this template.  The context passed in is used to resolve
				all expressions with the template.
		"""
		# This method must wrap outputFile if required by the encoding, and write out
		# any template pre-amble (DTD, Encoding, etc)
		
		# Write out the XML prolog
		encodingFile = codecs.lookup (outputEncoding)[3](outputFile)
		if (outputEncoding.lower() != "utf-8"):
			encodingFile.write ('<?xml version="1.0" encoding="%s"?>\n' % outputEncoding.lower())
		else:
			encodingFile.write ('<?xml version="1.0"?>\n')
		self.expandInline (context, encodingFile)
		
def tagAsText ((tag,atts)):
	result = "<" + tag 
	for att in atts:
		result += ' ' + att[0] + '="' + att[1] + '"'
	result += ">"
	return result
	
class TemplateCompiler:
	def __init__ (self):
		self.commandList = []
		self.tagStack = []
		self.symbolLocationTable = {}
		self.endTagSymbol = 1
		
		self.commandHandler  = {}
		self.commandHandler [TAL_DEFINE] = self.compileCmdDefine;
		self.commandHandler [TAL_CONDITION] = self.compileCmdCondition;
		self.commandHandler [TAL_REPEAT] = self.compileCmdRepeat;
		self.commandHandler [TAL_CONTENT] = self.compileCmdContent;
		self.commandHandler [TAL_REPLACE] = self.compileCmdReplace;
		self.commandHandler [TAL_ATTRIBUTES] = self.compileCmdAttributes;
		self.commandHandler [TAL_OMITTAG] = self.compileCmdOmitTag;
		
		self.log = logging.getLogger ("simpleTAL.TemplateCompiler")

	def getTemplate (self):
		return Template (self.commandList, self.symbolLocationTable)
		
	def addCommand (self, command):
		if (command[0] == TAL_OUTPUT and (len (self.commandList) > 1) and self.commandList[-1][0] == TAL_OUTPUT):
			# We can combine output commands
			self.commandList[-1] = (TAL_OUTPUT, self.commandList[-1][1] + command[1])
		else:
			self.commandList.append (command)
		
	def addTag (self, tag, originalAtts=None, command=None):
		""" Used to add a tag and (optionally) a TAL command.
				TAGS are (tagName, attribute) list tuples.
		"""
		# Add the tag to the tagStack
		self.log.debug ("Adding tag %s to stack" % tag[0])
		if (command is not None):
			self.tagStack.append ((tag, self.endTagSymbol))
		else:
			self.tagStack.append ((tag, None))
		if (command is not None):
			# All tags that have a TAL attribute on them start with a 'start scope'
			self.addCommand((TAL_START_SCOPE, (originalAtts, tag[1])))
			# Now we add the TAL command
			self.addCommand(command)
		else:
			# It's just a straight output, so create an output command and append it
			self.addCommand((TAL_OUTPUT, tagAsText (tag)))
	
	def popTag (self, tag, omitTagFlag=0):
		""" omitTagFlag is used to control whether the end tag should be included in the
				output or not.  In HTML 4.01 there are several tags which should never have
				end tags, this flag allows the template compiler to specify that these
				should not be output.
		"""
		while (len (self.tagStack) > 0):
			oldTag, endTagSymbol = self.tagStack.pop()
			self.log.debug ("Popped tag %s off stack" % oldTag[0])
			if (oldTag[0] == tag[0]):
				# We've found the right tag, now check to see if we have any TAL commands on it
				if (endTagSymbol is not None):					
					# We have a command (it's a TAL tag)
					# Note where the end tag symbol should point (i.e. the next command)
					self.symbolLocationTable [endTagSymbol] = len (self.commandList)
					
					# We need a "close scope and tag" command
					self.addCommand((TAL_ENDTAG_ENDSCOPE, (tag[0], omitTagFlag)))
					return
				elif (omitTagFlag == 0):
					# We are popping off an un-interesting tag, just add the close as text
					self.addCommand((TAL_OUTPUT, '</' + tag[0] + '>'))
					return
				else:
					# We are suppressing the output of this tag, so just return
					return
			else:	
				# We have a different tag, which means something like <br> which never closes is in 
				# between us and the real tag.
				
				# If the tag that we did pop off has a command though it means un-ballanced TAL tags!
				if (endTagSymbol is not None):
					# ERROR
					msg = "TAL Elements must be ballanced - found close tag %s expecting %s" % (oldTag[0], tag[0])
					self.log.error (msg)
					raise TemplateParseException (tagAsText(oldTag), msg)
					
	def parseStartTag (self, tag, attributes):
		# Note down the tag we are handling, it will be used for error handling during
		# compilation
		self.currentStartTag = (tag, attributes)
	
		# Look for tal attributes
		foundTALAtts = {}
		cleanAttributes = []
		for att in attributes:
			if (TAL_ATTRIBUTE_MAP.has_key (att[0])):
				# It's a TAL attribute
				foundTALAtts [TAL_ATTRIBUTE_MAP [att[0]]] = att[1]
			else:
				cleanAttributes.append (att)
				
		# This might be just content
		if (len (foundTALAtts) == 0):
			# Just content, add it to the various stacks
			self.addTag ((tag, cleanAttributes))
			return
			
		# Create a symbol for the end of the tag - we don't know what the offset is yet
		self.endTagSymbol += 1

		# Sort the tags by priority
		orderedTalAtts = foundTALAtts.keys()
		orderedTalAtts.sort()
		firstTag = 1
		for talAtt in orderedTalAtts:
			# Parse and create a command for each 
			cmnd = self.commandHandler [talAtt](foundTALAtts[talAtt])
			if (cmnd is None):
				self.log.error ("Command constant %s returned None" % str (talAtt))
				raise "Fatal internal error"
				
			if (firstTag):
				# The first one needs to add the tag
				firstTag = 0
				self.addTag ((tag, cleanAttributes), attributes, cmnd)
			else:
				# All others just append
				self.addCommand(cmnd)
				
		# Add the start tag command in as a child of the last TAL command
		self.addCommand((TAL_STARTTAG, tag))
		
	def parseEndTag (self, tag):
		""" Just pop the tag and related commands off the stack. """
		self.popTag ((tag,None))
		
	def parseData (self, data):
		# Just add it as an output
		self.addCommand((TAL_OUTPUT, data))
						
	def compileCmdDefine (self, argument):
		# Compile a define command, resulting argument is:
		# [(isLocalFlag (Y/n), variableName, variablePath),...]
		# Break up the list of defines first
		commandArgs = []
		for defineStmt in argument.split (';'):
			# Break each defineStmt into pieces "[local|global] varName expression"
			stmtBits = defineStmt.split (' ')
			isLocal = 1
			if (len (stmtBits) < 2):
				# Error, badly formed define command
				msg = "Badly formed define command '%s'.  Define commands must be of the form: '[local|global] varName expression[;[local|global] varName expression]'" % argument
				self.log.error (msg)
				raise TemplateParseException (tagAsText (self.currentStartTag), msg)
			# Assume to start with that >2 elements means a local|global flag
			if (len (stmtBits) > 2):
				if (stmtBits[0] == 'global'):
					isLocal = 0
					varName = stmtBits[1]
					expression = string.join (stmtBits[2:], ' ')
				elif (stmtBits[0] == 'local'):
					varName = stmtBits[1]
					expression = string.join (stmtBits[2:], ' ')
				else:
					# Must be a space in the expression that caused the >3 thing
					varName = stmtBits[0]
					expression = string.join (stmtBits[1:], ' ')
			else:
				# Only two bits
				varName = stmtBits[0]
				expression = string.join (stmtBits[1:], ' ')
			
			commandArgs.append ((isLocal, varName, expression))
		return (TAL_DEFINE, commandArgs)
		
	def compileCmdCondition (self, argument):
		# Compile a condition command, resulting argument is:
		# path, endTagSymbol
		# Sanity check
		if (len (argument) == 0):
			# No argument passed
			msg = "No argument passed!  condition commands must be of the form: 'path'"
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
	
		return (TAL_CONDITION, (argument, self.endTagSymbol))
		
	def compileCmdRepeat (self, argument):
		# Compile a repeat command, resulting argument is:
		# (varname, expression, endTagSymbol)
		attProps = argument.split (' ')
		if (len (attProps) < 2):
			# Error, badly formed repeat command
			msg = "Badly formed repeat command '%s'.  Repeat commands must be of the form: 'localVariable path'" % argument
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
			
		varName = attProps [0]
		expression = string.join (attProps[1:])
		return (TAL_REPEAT, (varName, expression, self.endTagSymbol))
	
	def compileCmdContent (self, argument, replaceFlag=0):
		# Compile a content command, resulting argument is
		# (replaceFlag, structureFlag, expression, endTagSymbol)
		
		# Sanity check
		if (len (argument) == 0):
			# No argument passed
			msg = "No argument passed!  content/replace commands must be of the form: 'path'"
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
	  	
		structureFlag = 0
		attProps = argument.split (' ')
		if (len(attProps) > 1):
			if (attProps[0] == "structure"):
				structureFlag = 1
				express = string.join (attProps[1:])
			elif (attProps[1] == "text"):
				structureFlag = 0
				express = string.join (attProps[1:])
			else:
				# It's not a type selection after all - assume it's part of the path
				express = argument
		else:
			express = argument
		return (TAL_CONTENT, (replaceFlag, structureFlag, express, self.endTagSymbol))
		
	def compileCmdReplace (self, argument):
		return self.compileCmdContent (argument, replaceFlag=1)
		
	def compileCmdAttributes (self, argument):
		# Compile tal:attributes into attribute command
		# Argument: [(attributeName, expression)]
		
		# Break up the list of attribute settings first
		commandArgs = []
		for attributeStmt in argument.split (';'):
			# Break each attributeStmt into name and expression
			stmtBits = attributeStmt.split (' ')
			if (len (stmtBits) < 2):
				# Error, badly formed attributes command
				msg = "Badly formed attributes command '%s'.  Attributes commands must be of the form: 'name expression[;name expression]'" % argument
				self.log.error (msg)
				raise TemplateParseException (tagAsText (self.currentStartTag), msg)
			attName = stmtBits[0]
			attExpr = string.join (stmtBits[1:],' ')
			commandArgs.append ((attName, attExpr))
		return (TAL_ATTRIBUTES, commandArgs)
		
	def compileCmdOmitTag (self, argument):
		# Compile a condition command, resulting argument is:
		# path
		# If no argument is given then set the path to default
		if (len (argument) == 0 or argument == "tal:omit-tag"):
			expression = "default"
		else:
			expression = argument
		
		return (TAL_OMITTAG, expression)

class TemplateParseException (Exception):
	def __init__ (self, location, errorDescription):
		self.location = location
		self.errorDescription = errorDescription
		
	def __str__ (self):
		return "[" + self.location + "] " + self.errorDescription

# The list of elements in HTML that can not have end tags - done as a dictionary for fast
# lookup.	
HTML_FORBIDDEN_ENDTAG = {'AREA': 1, 'BASE': 1, 'BASEFONT': 1, 'BR': 1, 'COL': 1
												,'FRAME': 1, 'HR': 1, 'IMG': 1, 'INPUT': 1, 'ISINDEX': 1
												,'LINK': 1, 'META': 1, 'PARAM': 1}

class HTMLTemplateCompiler (TemplateCompiler, sgmllib.SGMLParser):
	def __init__ (self):
		TemplateCompiler.__init__ (self)
		sgmllib.SGMLParser.__init__ (self)
		self.log = logging.getLogger ("simpleTAL.HTMLTemplateCompiler")
		
	def parseTemplate (self, file, encoding="iso8859-1"):
		encodedFile = codecs.lookup (encoding)[2](file)
		self.encoding = encoding
		self.feed (encodedFile.read())
		self.close()
		
	def unknown_starttag (self, tag, attributes):
		self.log.debug ("Recieved Start Tag: " + tag + " Attributes: " + str (attributes))
		if (HTML_FORBIDDEN_ENDTAG.has_key (tag.upper())):
			# This should have no end tag, so we just do the start and suppress the end
			self.parseStartTag (tag, attributes)
			self.log.debug ("End tag forbidden, generating close tag with no output.")
			self.popTag ((tag, None), omitTagFlag=1)
		else:
			self.parseStartTag (tag, attributes)
		
	def unknown_endtag (self, tag):
		self.log.debug ("Recieved End Tag: " + tag)
		if (HTML_FORBIDDEN_ENDTAG.has_key (tag.upper())):
			self.log.warn ("HTML 4.01 forbids end tags for the %s element" % tag)
		else:
			# Normal end tag
			self.popTag ((tag, None))
			
	def handle_data (self, data):
		self.log.debug ("Recieved Real Data: " + data)
		self.parseData (cgi.escape (data))
		
	# These two methods are required so that we pass through entity references that we don't
	# know about.  NOTE:  They are not escaped on purpose.
	def handle_charref (self, ref):
		self.parseData (u'&#%s;' % ref)
		
	def handle_entityref (self, ref):
		self.parseData (u'&%s;' % ref)
			
	def getTemplate (self):
		return HTMLTemplate (self.commandList, self.symbolLocationTable)
			
class XMLTemplateCompiler (TemplateCompiler, xml.sax.handler.ContentHandler):
	def __init__ (self):
		TemplateCompiler.__init__ (self)
		xml.sax.handler.ContentHandler.__init__ (self)
		self.log = logging.getLogger ("simpleTAL.XMLTemplateCompiler")
		
	def parseTemplate (self, file):
		xml.sax.parse (file, self)

	def startElement (self, tag, attributes):
		self.log.debug ("Recieved Real Start Tag: " + tag + " Attributes: " + str (attributes))
		# Convert attributes into a list of tuples
		atts = []
		for att in attributes.keys():
			atts.append ((att, attributes [att]))
		self.parseStartTag (tag, atts)
	
	def endElement (self, tag):
		self.log.debug ("Recieved Real End Tag: " + tag)
		self.parseEndTag (tag)
		
	def characters (self, data):
		self.log.debug ("Recieved Real Data: " + data)
		# Escape any data we recieve - we don't want any: <&> in there.
		self.parseData (cgi.escape (data))
		
	def getTemplate (self):
		return XMLTemplate (self.commandList, self.symbolLocationTable)
			
def compileHTMLTemplate (template, inputEncoding="ISO8859-1"):
	""" Reads the templateFile and produces a compiled template.
			To use the resulting template object call:
				template.expand (context, outputFile)
	"""
	if (isinstance (template, type (""))):
		# It's a string!
		templateFile = StringIO.StringIO (template)
	else:
		templateFile = template
	compiler = HTMLTemplateCompiler()
	compiler.parseTemplate (templateFile, inputEncoding)
	return compiler.getTemplate()

def compileXMLTemplate (template):
	""" Reads the templateFile and produces a compiled template.
			To use the resulting template object call:
				template.expand (context, outputFile)
	"""
	if (isinstance (template, type (""))):
		# It's a string!
		templateFile = StringIO.StringIO (template)
	else:
		templateFile = template
	compiler = XMLTemplateCompiler()
	compiler.parseTemplate (templateFile)
	return compiler.getTemplate()
	