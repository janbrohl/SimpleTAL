""" simpleTAL Interpreter

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial
		use.  No warranties, expressed or implied, are made as to the
		fitness of this code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		
		The classes in this module implement the TAL language, expanding
		both XML and HTML templates.
		
		Module Dependencies: logging, simpleTALES, simpleTALTemplates
"""

__version__ = "3.1"

try:
	import logging
except:
	import DummyLogger as logging
	
import sgmllib, xml.sax, cgi, string, StringIO, codecs, re

import simpleTALES

# Name-space URIs
METAL_NAME_URI="http://xml.zope.org/namespaces/metal"
TAL_NAME_URI="http://xml.zope.org/namespaces/tal"
	
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

# METAL Starts here
# Argument: expression, slotParams, endTagSymbol
METAL_USE_MACRO = 14
# Argument: macroName, endTagSymbol
METAL_DEFINE_SLOT=15
# Only used for parsing
METAL_FILL_SLOT=16
METAL_DEFINE_MACRO=17
											
METAL_NAME_REGEX = re.compile ("[a-zA-Z_][a-zA-Z0-9_]*")
									  
class TemplateInterpreter:
	def __init__ (self):
		self.programStack = []
		self.commandList = None
		self.symbolTable = None
		self.slotParameters = {}
		self.commandHandler  = {}
		self.commandHandler [TAL_DEFINE] = self.cmdDefine
		self.commandHandler [TAL_CONDITION] = self.cmdCondition
		self.commandHandler [TAL_REPEAT] = self.cmdRepeat
		self.commandHandler [TAL_CONTENT] = self.cmdContent
		self.commandHandler [TAL_ATTRIBUTES] = self.cmdAttributes
		self.commandHandler [TAL_OMITTAG] = self.cmdOmitTag
		self.commandHandler [TAL_START_SCOPE] = self.cmdStartScope
		self.commandHandler [TAL_OUTPUT] = self.cmdOutput
		self.commandHandler [TAL_STARTTAG] = self.cmdOutputStartTag
		self.commandHandler [TAL_ENDTAG_ENDSCOPE] = self.cmdEndTagEndScope
		self.commandHandler [METAL_USE_MACRO] = self.cmdUseMacro
		self.commandHandler [METAL_DEFINE_SLOT] = self.cmdDefineSlot
		self.commandHandler [TAL_NOOP] = self.cmdNoOp
	
	def initialise (self, context, outputFile):
		self.context = context
		self.file = outputFile
		
	def cleanState (self):
		self.scopeStack = []
		self.programCounter = 0
		self.movePCForward = None
		self.movePCBack = None
		self.outputTag = 1
		self.originalAttributes = []
		self.currentAttributes = []
		self.currentSlots = {}
		self.repeatVariable = None
		self.repeatIndex = 0
		self.repeatSequence = None
		self.tagContent = None
		# tagState flag as to whether there are any local variables to pop
		self.localVarsDefined = 0
		# Pass in the parameters
		self.currentSlots = self.slotParameters
		
	def popProgram (self):
		vars, self.commandList, self.symbolTable = self.programStack.pop()
		self.programCounter,self.scopeStack,self.slotParameters,self.currentSlots, self.movePCForward,self.movePCBack,self.outputTag,self.originalAttributes,self.currentAttributes,self.repeatVariable,self.repeatIndex,self.repeatSequence,self.tagContent,self.localVarsDefined = vars
		
	def pushProgram (self):
		vars = (self.programCounter
					 ,self.scopeStack
		       ,self.slotParameters
		       ,self.currentSlots
					 ,self.movePCForward
					 ,self.movePCBack
					 ,self.outputTag
					 ,self.originalAttributes
					 ,self.currentAttributes
					 ,self.repeatVariable
					 ,self.repeatIndex
					 ,self.repeatSequence
					 ,self.tagContent
					 ,self.localVarsDefined)
		self.programStack.append ((vars,self.commandList, self.symbolTable))

	def execute (self, template):
		self.cleanState()
		self.commandList, self.programCounter, programLength, self.symbolTable = template.getProgram()
		cmndList = self.commandList
		while (self.programCounter < programLength):
			cmnd = cmndList [self.programCounter]
			#print "PC: %s  -  Executing command: %s" % (str (self.programCounter), str (cmnd))
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
			self.tagContent = None
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
				# Suppress the final close tag and content
				self.tagContent = None
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
				
		if (self.movePCForward is not None):
			self.programCounter = self.movePCForward
			return
		self.programCounter += 1
		return
	
	def cmdEndTagEndScope (self, command, args):
		# Args: tagName, omitFlag
		if (self.tagContent is not None):
			contentType, resultVal = self.tagContent
			if (contentType):
				if (isinstance (resultVal, Template)):
					# We have another template in the context, evaluate it!
					# Save our state!
					self.pushProgram()
					resultVal.expandInline (self.context, self.file, self)
					# Restore state
					self.popProgram()
					# End of the macro expansion (if any) so clear the parameters
					self.slotParameters = {}
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
		
	def cmdUseMacro (self, command, args):
		""" args: (macroExpression, slotParams, endTagSymbol)
				Evaluates the expression, if it resolves to a SubTemplate it then places
				the slotParams into currentSlots and then jumps to the end tag
		"""
		result = self.context.evaluate (args[0], self.originalAttributes)
		if (result is None or result.isNothing()):
			# Don't output anything
			self.outputTag = 0
			# Output none of our content or the existing content
			self.movePCForward = self.symbolTable [args[2]]
			self.programCounter += 1
			return
		value = result.value()
		if (not result.isDefault() and isinstance (value, SubTemplate)):
			# We have a macro, so let's use it
			self.outputTag = 0
			self.slotParameters = args[1]
			self.tagContent = (1, value)
			# NOTE: WE JUMP STRAIGHT TO THE END TAG, NO OTHER TAL/METAL COMMANDS ARE EVALUATED.
			self.programCounter = self.symbolTable [args[2]]
			return
		else:
			# Default, let's just run through as normal
			self.programCounter += 1
			return
			
	def cmdDefineSlot (self, command, args):
		""" args: (slotName, endTagSymbol)
				If the slotName is filled then that is used, otherwise the original conent
				is used.
		"""
		if (self.currentSlots.has_key (args[0])):
			# This slot is filled, so replace us with that content
			self.outputTag = 0
			self.tagContent = (1, self.currentSlots [args[0]])
			# Output none of our content or the existing content
			# NOTE: NO FURTHER TAL/METAL COMMANDS ARE EVALUATED
			self.programCounter = self.symbolTable [args[1]]
			return
		# Slot isn't filled, so just use our own content
		self.programCounter += 1
		return
	
class Template:
	def __init__ (self, commands, macros, symbols):
		self.commandList = commands
		self.macros = macros
		self.symbolTable = symbols
		
		# Setup the macros
		for macro in self.macros.values():
			macro.setParentTemplate (self)
			
		# Setup the slots
		for cmnd, arg in self.commandList:
			if (cmnd == METAL_USE_MACRO):
				# Set the parent of each slot
				slotMap = arg[1]
				for slot in slotMap.values():
					slot.setParentTemplate (self)

	def expand (self, context, outputFile, outputEncoding=None, interpreter=None):
		""" This method will write to the outputFile, using the encoding specified,
				the expanded version of this template.  The context passed in is used to resolve
				all expressions with the template.
		"""
		# This method must wrap outputFile if required by the encoding, and write out
		# any template pre-amble (DTD, Encoding, etc)
		self.expandInline (context, outputFile, interpreter)
		
	def expandInline (self, context, outputFile, interpreter=None):
		""" Internally used when expanding a template that is part of a context."""
		if (interpreter is None):
			ourInterpreter = TemplateInterpreter()
			ourInterpreter.initialise (context, outputFile)
		else:
			ourInterpreter = interpreter
		ourInterpreter.execute (self)

	def getProgram (self):
		""" Returns a tuple of (commandList, startPoint, endPoint, symbolTable) """
		return (self.commandList, 0, len (self.commandList), self.symbolTable)
		
	def __str__ (self):
		result = "Commands:\n"
		index = 0
		for cmd in self.commandList:
			if (cmd[0] != METAL_USE_MACRO):
				result = result + "\n[%s] %s" % (str (index), str (cmd))
			else:
				result = result + "\n[%s] %s, (%s{" % (str (index), str (cmd[0]), str (cmd[1][0]))
				for slot in cmd[1][1].keys():
					result = result + "%s: %s" % (slot, str (cmd[1][1][slot]))
				result = result + "}, %s)" % str (cmd[1][2])
			index += 1
		result = result + "\n\nSymbols:\n"
		for symbol in self.symbolTable.keys():
			result = result + "Symbol: " + str (symbol) + " points to: " + str (self.symbolTable[symbol]) + ", which is command: " + str (self.commandList[self.symbolTable[symbol]]) + "\n"	
		
		result = result + "\n\nMacros:\n"
		for macro in self.macros.keys():
			result = result + "Macro: " + str (macro) + " value of: " + str (self.macros[macro])
		return result
		
class SubTemplate (Template):
	""" A SubTemplate is part of another template, and is used for the METAL implementation.
			The two uses for this class are:
				1 - metal:define-macro results in a SubTemplate that is the macro
				2 - metal:fill-slot results in a SubTemplate that is a parameter to metal:use-macro
	"""
	def __init__ (self, startRange, endRangeSymbol):
		""" The parentTemplate is the template for which we are a sub-template.
				The startRange and endRange are indexes into the parent templates command list, 
				and defines the range of commands that we can execute
		"""
		Template.__init__ (self, [], {}, {})
		self.startRange = startRange
		self.endRangeSymbol = endRangeSymbol
		
	def setParentTemplate (self, parentTemplate):
		self.parentTemplate = parentTemplate
		self.commandList = parentTemplate.commandList
		self.symbolTable = parentTemplate.symbolTable
		
	def getProgram (self):
		""" Returns a tuple of (commandList, startPoint, endPoint, symbolTable) """
		return (self.commandList, self.startRange, self.symbolTable[self.endRangeSymbol]+1, self.symbolTable)
						
	def __str__ (self):
		endRange = self.symbolTable [self.endRangeSymbol]
		result = "SubTemplate from %s to %s\n" % (str (self.startRange), str (endRange))
		return result
		
class HTMLTemplate (Template):
	"""A specialised form of a template that knows how to output HTML
	"""
	
	def expand (self, context, outputFile, outputEncoding="ISO-8859-1",interpreter=None):
		""" This method will write to the outputFile, using the encoding specified,
				the expanded version of this template.  The context passed in is used to resolve
				all expressions with the template.
		"""
		# This method must wrap outputFile if required by the encoding, and write out
		# any template pre-amble (DTD, Encoding, etc)
		
		encodingFile = codecs.lookup (outputEncoding)[3](outputFile)
		self.expandInline (context, encodingFile, interpreter)
		
class XMLTemplate (Template):
	"""A specialised form of a template that knows how to output XML
	"""
	
	def expand (self, context, outputFile, outputEncoding="iso8859-1", interpreter=None):
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
		self.expandInline (context, encodingFile, interpreter)
		
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
		self.macroMap = {}
		self.endTagSymbol = 1
		
		self.commandHandler  = {}
		self.commandHandler [TAL_DEFINE] = self.compileCmdDefine
		self.commandHandler [TAL_CONDITION] = self.compileCmdCondition
		self.commandHandler [TAL_REPEAT] = self.compileCmdRepeat
		self.commandHandler [TAL_CONTENT] = self.compileCmdContent
		self.commandHandler [TAL_REPLACE] = self.compileCmdReplace
		self.commandHandler [TAL_ATTRIBUTES] = self.compileCmdAttributes
		self.commandHandler [TAL_OMITTAG] = self.compileCmdOmitTag
		
		# Metal commands
		self.commandHandler [METAL_USE_MACRO] = self.compileMetalUseMacro
		self.commandHandler [METAL_DEFINE_SLOT] = self.compileMetalDefineSlot
		self.commandHandler [METAL_FILL_SLOT] = self.compileMetalFillSlot
		self.commandHandler [METAL_DEFINE_MACRO] = self.compileMetalDefineMacro
		
		# Default namespaces
		self.setTALPrefix ('tal')
		self.tal_namespace_prefix_stack = []
		self.metal_namespace_prefix_stack = []
		self.tal_namespace_prefix_stack.append ('tal')
		self.setMETALPrefix ('metal')
		self.metal_namespace_prefix_stack.append ('metal')
		
		self.log = logging.getLogger ("simpleTAL.TemplateCompiler")
		
	def setTALPrefix (self, prefix):
		self.tal_namespace_prefix = prefix
		self.tal_attribute_map = {}
		self.tal_attribute_map ['%s:attributes'%prefix] = TAL_ATTRIBUTES
		self.tal_attribute_map ['%s:content'%prefix]= TAL_CONTENT
		self.tal_attribute_map ['%s:define'%prefix] = TAL_DEFINE
		self.tal_attribute_map ['%s:replace'%prefix] = TAL_REPLACE
		self.tal_attribute_map ['%s:omit-tag'%prefix] = TAL_OMITTAG
		self.tal_attribute_map ['%s:condition'%prefix] = TAL_CONDITION
		self.tal_attribute_map ['%s:repeat'%prefix] = TAL_REPEAT
		
	def setMETALPrefix (self, prefix):
		self.metal_namespace_prefix = prefix
		self.metal_attribute_map = {}
		self.metal_attribute_map ['%s:define-macro'%prefix] = METAL_DEFINE_MACRO
		self.metal_attribute_map ['%s:use-macro'%prefix] = METAL_USE_MACRO
		self.metal_attribute_map ['%s:define-slot'%prefix] = METAL_DEFINE_SLOT
		self.metal_attribute_map ['%s:fill-slot'%prefix] = METAL_FILL_SLOT
		
	def popTALNamespace (self):
		newPrefix = self.tal_namespace_prefix_stack.pop()
		self.setTALPrefix (newPrefix)
		
	def popMETALNamespace (self):
		newPrefix = self.metal_namespace_prefix_stack.pop()
		self.setMETALPrefix (newPrefix)
		
	def getTemplate (self):
		template = Template (self.commandList, self.macroMap, self.symbolLocationTable)
		return template
		
	def addCommand (self, command):
		if (command[0] == TAL_OUTPUT and (len (self.commandList) > 0) and self.commandList[-1][0] == TAL_OUTPUT):
			# We can combine output commands
			self.commandList[-1] = (TAL_OUTPUT, self.commandList[-1][1] + command[1])
		else:
			self.commandList.append (command)
		
	def addTag (self, tag, tagProperties={}):
		""" Used to add a tag to the stack.  Various properties can be passed in the dictionary
		    as being information required by the tag.
		    Currently supported properties are:
		    		'command'         - The (command,args) tuple associated with this command
		    		'originalAtts'    - The original attributes that include any metal/tal attributes
		    		'endTagSymbol'    - The symbol associated with the end tag for this element
		    		'popFunctionList' - A list of functions to execute when this tag is popped
		"""
		# Add the tag to the tagStack (list of tuples (tag, properties, useMacroLocation))
		self.log.debug ("Adding tag %s to stack" % tag[0])
		command = tagProperties.get ('command',None)
		originalAtts = tagProperties.get ('originalAtts', None)
		if (command is not None):
			if (command[0] == METAL_USE_MACRO):
				self.tagStack.append ((tag, tagProperties, len (self.commandList)+1))
			else:
				self.tagStack.append ((tag, tagProperties, None))
		else:
			self.tagStack.append ((tag, tagProperties, None))
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
			oldTag, tagProperties, useMacroLocation = self.tagStack.pop()
			endTagSymbol = tagProperties.get ('endTagSymbol', None)
			popCommandList = tagProperties.get ('popFunctionList', [])
			for func in popCommandList:
				apply (func, ())
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
				
				# If the tag that we did pop off has a command though it means un-balanced TAL tags!
				if (endTagSymbol is not None):
					# ERROR
					msg = "TAL/METAL Elements must be balanced - found close tag %s expecting %s" % (tag[0], oldTag[0])
					self.log.error (msg)
					raise TemplateParseException (tagAsText(oldTag), msg)
		self.log.error ("Close tag %s found with no corresponding open tag." % tag[0])
		raise TemplateParseException ("</%s>" % tag[0], "Close tag encountered with no corresponding open tag.")
					
	def parseStartTag (self, tag, attributes):
		# Note down the tag we are handling, it will be used for error handling during
		# compilation
		self.currentStartTag = (tag, attributes)

		# Look for tal/metal attributes
		foundTALAtts = []
		foundMETALAtts = []
		foundCommandsArgs = {}
		cleanAttributes = []
		tagProperties = {}
		popTagFuncList = []
		TALElementNameSpace = 0
		prefixToAdd = ""
		
		# Determine whether this element is in either the METAL or TAL namespace
		if (tag.find (':') > 0):
			# We have a namespace involved, so let's look to see if its one of ours
			namespace = tag[0:tag.find (':')]
			if (namespace == self.metal_namespace_prefix):
				TALElementNameSpace = 1
				prefixToAdd = self.metal_namespace_prefix +":"
			elif (namespace == self.tal_namespace_prefix):
				TALElementNameSpace = 1
				prefixToAdd = self.tal_namespace_prefix +":"
			
			if (TALElementNameSpace):
				# We should treat this an implicit omit-tag
				foundTALAtts.append (TAL_OMITTAG)
				# Will go to default, i.e. yes
				foundCommandsArgs [TAL_OMITTAG] = ""
				
		for att, value in attributes:
			if (TALElementNameSpace and att[0:len (prefixToAdd)] != prefixToAdd):
				commandAttName = prefixToAdd + att
			else:
				commandAttName = att
			self.log.debug ("Command name is now %s" % commandAttName)
			if (att[0:5] == "xmlns"):
				# We have a namespace declaration.
				prefix = att[6:]
				if (value == METAL_NAME_URI):
					# It's a METAL namespace declaration
					if (len (prefix) > 0):
						self.metal_namespace_prefix_stack.append (self.metal_namespace_prefix)
						self.setMETALPrefix (prefix)
						# We want this function called when the scope ends
						popTagFuncList.append (self.popMETALNamespace)
					else:
						# We don't allow METAL/TAL to be declared as a default
						msg = "Can not use METAL name space by default, a prefix must be provided."
						raise TemplateParseException (tagAsText (self.currentStartTag), msg)
				elif (value == TAL_NAME_URI):
					# TAL this time
					if (len (prefix) > 0):
						self.tal_namespace_prefix_stack.append (self.tal_namespace_prefix)
						self.setTALPrefix (prefix)
						# We want this function called when the scope ends
						popTagFuncList.append (self.popTALNamespace)
					else:
						# We don't allow METAL/TAL to be declared as a default
						msg = "Can not use TAL name space by default, a prefix must be provided."
						raise TemplateParseException (tagAsText (self.currentStartTag), msg)
				else:
					# It's nothing special, just an ordinary namespace declaration
					cleanAttributes.append ((att,value))
			elif (self.tal_attribute_map.has_key (commandAttName)):
				# It's a TAL attribute
				cmnd = self.tal_attribute_map [commandAttName]
				if (cmnd == TAL_OMITTAG and TALElementNameSpace):
					self.log.warn ("Supressing omit-tag command present on TAL or METAL element")
				else:
					foundCommandsArgs [cmnd] = value
					foundTALAtts.append (cmnd)
			elif (self.metal_attribute_map.has_key (commandAttName)):
				# It's a METAL attribute
				cmnd = self.metal_attribute_map [commandAttName]
				foundCommandsArgs [cmnd] = value
				foundMETALAtts.append (cmnd)
			else:
				cleanAttributes.append ((att,value))
		tagProperties ['popFunctionList'] = popTagFuncList

		# This might be just content
		if ((len (foundTALAtts) + len (foundMETALAtts)) == 0):
			# Just content, add it to the various stacks
			self.addTag ((tag, cleanAttributes), tagProperties)
			return
			
		# Create a symbol for the end of the tag - we don't know what the offset is yet
		self.endTagSymbol += 1
		tagProperties ['endTagSymbol'] = self.endTagSymbol
		
		# Sort the METAL commands
		foundMETALAtts.sort()
		# Sort the tags by priority
		foundTALAtts.sort()
		
		# We handle the METAL before the TAL
		allCommands = foundMETALAtts + foundTALAtts
		firstTag = 1
		for talAtt in allCommands:
			# Parse and create a command for each 
			cmnd = self.commandHandler [talAtt](foundCommandsArgs[talAtt])
			if (cmnd is not None):
				if (firstTag):
					# The first one needs to add the tag
					firstTag = 0
					tagProperties ['originalAtts'] = attributes
					tagProperties ['command'] = cmnd
					self.addTag ((tag, cleanAttributes), tagProperties)
				else:
					# All others just append
					self.addCommand(cmnd)
		
		if (firstTag):
			tagProperties ['originalAtts'] = attributes
			tagProperties ['command'] = (TAL_STARTTAG, tag)
			self.addTag ((tag, cleanAttributes), tagProperties)
		else:		
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
		if (len (argument) == 0):
			expression = "default"
		else:
			expression = argument
		return (TAL_OMITTAG, expression)
		
	# METAL compilation commands go here
	def compileMetalUseMacro (self, argument):
		# Sanity check
		if (len (argument) == 0):
			# No argument passed
			msg = "No argument passed!  use-macro commands must be of the form: 'use-macro: path'"
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
		cmnd = (METAL_USE_MACRO, (argument, {}, self.endTagSymbol))
		self.log.debug ("Returning METAL_USE_MACRO: %s" % str (cmnd))
		return cmnd
		
	def compileMetalDefineMacro (self, argument):
		if (len (argument) == 0):
			# No argument passed
			msg = "No argument passed!  define-macro commands must be of the form: 'define-macro: name'"
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
			
		# Check that the name of the macro is valid
		if (METAL_NAME_REGEX.match (argument).end() != len (argument)):
			msg = "Macro name %s is invalid." % argument
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
		if (self.macroMap.has_key (argument)):
			msg = "Macro name %s is already defined!" % argument
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
			
		# The macro starts at the next command.
		macro = SubTemplate (len (self.commandList), self.endTagSymbol)
		self.macroMap [argument] = macro
		return None
		
	def compileMetalFillSlot (self, argument):
		if (len (argument) == 0):
			# No argument passed
			msg = "No argument passed!  fill-slot commands must be of the form: 'fill-slot: name'"
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
		
		# Check that the name of the macro is valid
		if (METAL_NAME_REGEX.match (argument).end() != len (argument)):
			msg = "Slot name %s is invalid." % argument
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
			
		# Determine what use-macro statement this belongs to by working through the list backwards
		ourMacroLocation = None
		location = len (self.tagStack) - 1
		while (ourMacroLocation is None):
			macroLocation = self.tagStack[location][2]
			if (macroLocation is not None):
				ourMacroLocation = macroLocation
			else:
				location -= 1
				if (location < 0):
					msg = "metal:fill-slot must be used inside a metal:use-macro call"
					self.log.error (msg)
					raise TemplateParseException (tagAsText (self.currentStartTag), msg)
		
		# Get the use-macro command we are going to adjust
		cmnd, args = self.commandList [ourMacroLocation]
		self.log.debug ("Use macro argument: %s" % str (args))
		macroName, slotMap, endSymbol = args
		
		# Check that the name of the slot is valid
		if (METAL_NAME_REGEX.match (argument).end() != len (argument)):
			msg = "Slot name %s is invalid." % argument
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
		
		if (slotMap.has_key (argument)):
			msg = "Slot %s has already been filled!" % argument
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
		
		# The slot starts at the next command.
		slot = SubTemplate (len (self.commandList), self.endTagSymbol)
		slotMap [argument] = slot
		
		# Update the command
		self.commandList [ourMacroLocation] = (cmnd, (macroName, slotMap, endSymbol))
		return None
		
	def compileMetalDefineSlot (self, argument):
		if (len (argument) == 0):
			# No argument passed
			msg = "No argument passed!  define-slot commands must be of the form: 'name'"
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
		# Check that the name of the slot is valid
		if (METAL_NAME_REGEX.match (argument).end() != len (argument)):
			msg = "Slot name %s is invalid." % argument
			self.log.error (msg)
			raise TemplateParseException (tagAsText (self.currentStartTag), msg)
			
		return (METAL_DEFINE_SLOT, (argument, self.endTagSymbol))

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
		atts = []
		for att in attributes:
			if (att[0] == att[1]):
				self.log.debug ("The attribute value is the same as the name, setting to empty string")
				atts.append ((att[0], ""))
			else:
				atts.append (att)
			
		if (HTML_FORBIDDEN_ENDTAG.has_key (tag.upper())):
			# This should have no end tag, so we just do the start and suppress the end
			self.parseStartTag (tag, atts)
			self.log.debug ("End tag forbidden, generating close tag with no output.")
			self.popTag ((tag, None), omitTagFlag=1)
		else:
			self.parseStartTag (tag, atts)
		
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
		
	# Handle document type declarations
	def handle_decl (self, data):
		self.parseData (u'<!%s>' % data)
		
	# Pass comments through un-affected.
	def handle_comment (self, data):
		self.parseData (u'<!--%s-->' % data)
		
	def report_unbalanced (self, tag):
		self.log.warn ("End tag %s present with no corresponding open tag.")
			
	def getTemplate (self):
		template = HTMLTemplate (self.commandList, self.macroMap, self.symbolLocationTable)
		return template
			
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
		#self.log.debug ("Recieved Real Data: " + data)
		# Escape any data we recieve - we don't want any: <&> in there.
		self.parseData (cgi.escape (data))
		
	def processingInstruction (self, target, data):
		self.log.debug ("Recieved processing instruction.")
		self.parseData (u'<?%s %s?>' % (target, data))
		
	def getTemplate (self):
		template = XMLTemplate (self.commandList, self.macroMap, self.symbolLocationTable)
		return template
			
def compileHTMLTemplate (template, inputEncoding="ISO8859-1"):
	""" Reads the templateFile and produces a compiled template.
			To use the resulting template object call:
				template.expand (context, outputFile)
	"""
	if (isinstance (template, type ("")) or isinstance (template, type (u""))):
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
	
