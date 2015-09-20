""" simpleTAL Interpreter

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commerical and non-commerical use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		
		The classes in this module implement the TAL language, expanding both
		XML and HTML templates.
		
		Module Dependencies: logging, simpleTALES
"""

__version__ = "1.1"

try:
	import logging
except:
	import DummyLogger as logging
	
import sgmllib, xml.sax, xml.sax.handler, xml.sax.saxutils, xml.sax.xmlreader
import string, StringIO
import copy

import simpleTALES
# See simpleTALES.py for ContextVariable and Context

def renderObject (anObj):
	if (type (anObj) == type (u"")):
		return anObj
	if (type (anObj) == type ("")):
		return unicode (anObj, 'ascii')
	return unicode (str (anObj), 'ascii')

class ElementStack:
	# Implements a stack of TagValues and TALHandlers
	def __init__ (self):
		self.elementStack = []
		self.log = logging.getLogger ("simpleTAL.ElementStack")
		
	def push (self, tagValue, handlerList):
		self.log.debug ("Adding %s to stack" % str (tagValue))
		self.elementStack.append ((tagValue, handlerList))
		
	def pop (self, tag):
		self.log.debug ("Looking to pop off tag %s" % tag)
		while (len (self.elementStack) > 0):
			tagVal, handlerList = self.elementStack.pop()
			
			# Is this close tag for this element?
			if (tagVal.getTag() == tag):
				# Found corresponding tag!
				return tagVal,handlerList
			
			# Check for any TAL elements that did not have a close tag
			for handler in handlerList:
				if (handler.getPriority() != 7):
					# Generate a stack description
					stackStr = ""
					for pair in self.elementStack:
						stackStr = stackStr + ":" + pair[0]
					self.log.error ("Stack contents when un-closed TAL attribute found: %s" % stackStr)
					raise Exception ("Elements with TAL attributes must have a close tag!")
		
		# Last element - return None!	
		return None
		
	def getCurrentTagValue (self):
		if (len (self.elementStack) > 0):
			lastElement = self.elementStack[-1:][0]
			return lastElement[0]
		else:
			return None
	
	def getDepth (self):
		return len (self.tagStack)
		
class TALOutput:
	def __init__ (self):
		self.suppressOutput = 0
		self.tagStack = []
		
	def suppress (self):
		return len (self.tagStack)
	
	def pushSuppressionTag (self, tag):
		self.tagStack.append (tag)
		
	def popSuppressionTag (self, tag):
		while (len (self.tagStack) > 0):
			stackTag = self.tagStack.pop()
			if (stackTag == tag):
				# Found corresponding tag
				return

class HTMLOuput (TALOutput):
	def __init__ (self, encoding):
		TALOutput.__init__ (self)
		self.text = u""
		self.encoding = encoding
		
	def startElement (self, tag, attributes):
		cStr = u""
		if (not self.suppressOutput):
			cStr=u'<' + tag
			for att in attributes:
				if (att[1] != None):
					cStr=cStr + u' ' + att[0] + u'="' + att[1] + u'"'
				else:
					cStr=cStr + u' ' + att[0] + u'=""'
			cStr=cStr + u'>'
			self.text = self.text + cStr
		
	def endElement (self, tag):
		if (not self.suppressOutput):
			self.text = self.text + u'</' + tag + u'>'
		
	def characters (self, text):
		if (not self.suppressOutput and text is not None):
			 self.text = self.text + xml.sax.saxutils.escape (text)
			 
	def getValue (self):
		return self.text.encode (self.encoding)
		
class XMLOutput (TALOutput, xml.sax.saxutils.XMLGenerator):
	def __init__ (self, file, encoding):
		TALOutput.__init__ (self)
		xml.sax.saxutils.XMLGenerator.__init__ (self, file, encoding)
		self.startDocument()
		
	def startElement (self, tag, attributes):
		# Need to sort out the attributes
		atMap = {}
		for at in attributes:
			atMap[at[0]] = at[1]
			
		atts = xml.sax.xmlreader.AttributesImpl(atMap)
		xml.sax.saxutils.XMLGenerator.startElement (self, tag, atts)

		
class TagValue:
	def __init__ (self, tag, attributes):
		self.tag = tag
		self.attributes = attributes
		self.originalAttributes = None
		self.originalAttsMap = None
		self.originalTagEnabled=1
		self.originalContentEnabled=1
		self.overrideText = ""
		
	def getTag (self):
		return self.tag
		
	def setOverrideCharacters (self, content):
		self.overrideText = content
		
	def getOverrideCharacters (self):
		return self.overrideText
		
	def setTagEnable (self, val):
		self.originalTagEnabled = val
		
	def getTagEnabled (self):
		return self.originalTagEnabled
		
	def setContentEnabled (self, val):
		self.originalContentEnabled = val
		
	def getContentEnabled (self):
		# Should original content of the tag be output?
		return self.originalContentEnabled
		
	def removeAttribute (self, attName):
		if (self.originalAttributes is None):
			# Lazy copy - only do this when required
			self.originalAttributes = copy.copy (self.attributes)
		for att in self.attributes:
			if (att[0] == attName):
				self.attributes.remove (att)
		
	def setAttribute (self, newAtt):
		if (self.originalAttributes is None):
			# Lazy copy - only do this when required
			self.originalAttributes = copy.copy (self.attributes)
			
		# If this attribute exists then we need to remove it first.
		for att in self.attributes:
			if (att[0] == newAtt[0]):
				self.attributes.remove (att)
				
		self.attributes.append (newAtt)
		
	def getAttributes (self):
		return self.attributes
		
	def getOriginalAttributes (self):
		# Only called on demand
		if (self.originalAttsMap is not None):
			return self.originalAttsMap
			
		if (self.originalAttributes is None):
			# Lazy copy - only do this when required
			self.originalAttributes = copy.copy (self.attributes)
		# Now produce the map
		map = {}
		for att in self.originalAttributes:
			map [att[0]] = att[1]
			
		self.originalAttsMap = map
		return map
		
	def findAttributeValue (self, attName):
		for att in self.attributes:
			if (att[0] == attName):
				return att[1]
		return None
		
	def __str__ (self):
		return "Tag: %s Attributes: %s" % (self.tag.encode ('ascii', 'replace'), str (self.attributes))
		
class TALHandler:
	def __init__ (self,handlerParam,eventHandler):
		self.eventHandler = eventHandler
		self.context = eventHandler.getContext()
		self.handlerParam = handlerParam
		
	def getPriority (self):
		return 7
		
	def handleStartTag (self, tagValue):
		# Return 'false' - suppression should be turned off
		return 0
		
	def handleEndTag (self, tagValue):
		# By default we do nothing
		pass
		
	def __cmp__ (self, other):
		return self.getPriority() - other.getPriority()
	
class TALOmitTag (TALHandler):
	def getPriority (self):
		return 7
		
	def handleStartTag (self, tagValue):
		log = logging.getLogger ("simpleTAL.TALOmitTag")
		tagValue.removeAttribute ("tal:omit-tag")
		
		omit = 0
		log.debug ("TAL Omit parameters: " + self.handlerParam)
		# If parameter is either empty or not-present then assume "yes"
		if ((len (self.handlerParam) == 0) or (self.handlerParam == "tal:omit-tag")):
			# If expression is undefined then omit the tag
			omit = 1
		else:
			temp = self.context.evaluate (self.handlerParam, tagValue.getOriginalAttributes)
			if (temp is None or temp.isTrue()):
				omit = 1
		if (omit):
			tagValue.setTagEnable (0)
		return 0
		
	def handleEndTag (self, tagValue):
		pass
		
class TALAttribute (TALHandler):
	def getPriority (self):
		return 5
		
	def handleStartTag (self, tagValue):
		# Remove our attribute ("tal:attributes") from the tagValue
		tagValue.removeAttribute ("tal:attributes")
		
		# Create any attributes we need
		for thingsToEvaluate in self.handlerParam.split (';'):
			# For each attribute that we have to set, get the name and value
			attProps = thingsToEvaluate.split (' ')
			attName = attProps[0]
			
			defaultValue = tagValue.findAttributeValue (attName)
			
			attValue = self.context.evaluate (string.join (attProps[1:]), tagValue.getOriginalAttributes)
			if (attValue is None or attValue.isNothing()):
				tagValue.removeAttribute (attName)
			elif (attValue.isDefault()):
				# Leave as it is currently - the defaultValue
				pass
			else:
				tagValue.setAttribute ((attName, renderObject (attValue.value())))
		return 0

	def handleEndTag (self, tagValue):
		pass
		
class TALContent (TALHandler):
	def getPriority (self):
		return 4
		
	def handleStartTag (self, tagValue):
		self.cleanAttributes (tagValue)
		# Get all the attributes things
		attProps = self.handlerParam.split(' ')

		# Assume text
		self.type = "text"
		if (len(attProps) > 1):
			if (attProps[0] == "structure"):
				self.type = "structure"
				self.expression = string.join (attProps[1:])
			elif (attProps[1] == "text"):
				self.type = "text"
				self.expression = string.join (attProps[1:])
			else:
				# It's not a type selection after all - assume it's part of the path
				self.expression = self.handlerParam
		else:
			self.expression = self.handlerParam
				
		evaluated = self.context.evaluate (self.expression, tagValue.getOriginalAttributes)
			
		# Override the text value!
		if (evaluated is None or evaluated.isNothing()):
			tagValue.setContentEnabled (0)
		elif (evaluated.isDefault()):
			tagValue.setContentEnabled (1)
		else:
			tagValue.setContentEnabled (0)
			if (self.type == "text"):
				tagValue.setOverrideCharacters (renderObject (evaluated.value()))
			else:
				self.evaluatedText = renderObject(evaluated.value())
		# We never suppress
		return 0
			
	def handleEndTag (self, tagValue):
		if (self.type == "structure"):
			# Re-enable content output
			tagValue.setContentEnabled (1)
			self.eventHandler.parseStructure (self.evaluatedText)
		
	def cleanAttributes (self, tagValue):
		# Remove our attribute ("tal:content") from the tagValue
		tagValue.removeAttribute ("tal:content")


class TALReplace (TALContent):
	def handleStartTag (self, tagValue):
		TALContent.handleStartTag (self, tagValue)
		# If content is being kept, then also keep the tag
		if (not tagValue.getContentEnabled()):
			tagValue.setTagEnable (0)
		return 0
	
	def cleanAttributes (self, tagValue):
		# Remove our attribute ("tal:replace") from the tagValue
		tagValue.removeAttribute ("tal:replace")

class TALRepeat (TALHandler):
	def getPriority (self):
		return 3
		
	def handleStartTag (self, tagValue):
		# Consume our tag
		tagValue.removeAttribute ("tal:repeat")
		self.localToPop = 0
		
		# Evaluate the params
		paramList = self.handlerParam.split (' ')
		expression = string.join (paramList[1:])
		evaluated = self.context.evaluate (expression, tagValue.getOriginalAttributes)
		if (evaluated is None or evaluated.isNothing()):
			self.repeat = 0
			# Suppress everything else!
			return 1
		elif (evaluated.isDefault()):
			self.repeat = 0
		elif (evaluated.isSequence()):
			self.repeat = 1
			self.ourList = evaluated.value()
			if (len (self.ourList) == 0):
				self.repeat = 0
				# Suppress everything else!
				return 1
			
			# We need to insert a recorder here.
			self.localVarName = paramList[0]
			self.ourListIndex = 0
			self.currentValue = self.ourList[self.ourListIndex]
			# Add the value for the first time around the loop
			self.localToPop = 1
			self.repeatVariable = simpleTALES.RepeatVariable (self.ourList)
			self.context.addRepeat (self.localVarName, self.repeatVariable)
			self.context.addLocals ([(self.localVarName, self.currentValue)])
			
			# Add a recorder to the event handler
			ourRecorder = EventRecorder(tagValue)
			self.eventHandler.pushRecorder(ourRecorder)
		else:
			self.repeat = 0
			# Suppress everything
			return 1
		return 0
		
	def handleEndTag (self, tagValue):
		if (not self.repeat):
			return
		
		# Remove our recorder
		self.ourRecorder = self.eventHandler.popRecorder(tagValue.getTag())
		self.eventHandler.setRepeatHook (self.replayHook)
		
	def replayHook (self):
		# Clear - otherwise we go into recursion
		self.eventHandler.clearRepeatHook()
		# Now replay  as many times as required
		while (self.ourListIndex < len (self.ourList) - 1):
			# Get the next value and sort out the local variables
			self.context.popLocals()
			self.ourListIndex += 1
			self.currentValue = self.ourList[self.ourListIndex]
			self.repeatVariable.increment()
			# Add the value for the first time around the loop
			self.context.addLocals ([(self.localVarName, self.currentValue)])
			# Now replay it
			self.ourRecorder.playBack (self.eventHandler)
		if (self.localToPop):
			self.context.popLocals()
			self.context.removeRepeat (self.localVarName)
		
	
class TALCondition (TALHandler):
	def handleStartTag (self, tagValue):
		tagValue.removeAttribute ("tal:condition")
		evaluated = self.context.evaluate (self.handlerParam, tagValue.getOriginalAttributes)
		if (evaluated is None or evaluated.isNothing()):
			# Suppress this element
			return 1
		elif (evaluated.isTrue()):
			return 0
		else:
			return 1
			
	def handleEndTag (self, tagValue):
		pass
		
	def getPriority (self):
		return 2

class TALDefine (TALHandler):
	def handleStartTag (self, tagValue):
		tagValue.removeAttribute ("tal:define")
		self.hasLocals = 0
		
		localsList = []
		for param in self.handlerParam.split (';'):
			paramParts = param.split (' ')
			scope = "local"
			if (len (paramParts) == 3):
				if (paramParts[0] == 'global'):
					scope = paramParts[0]
					del paramParts[0]
				elif (paramParts[0] == 'local'):
					del paramParts[0]
				
			result = self.context.evaluate (string.join (paramParts[1:]), tagValue.getOriginalAttributes)
			if (result is not None):
				result = result.value()
				
			if (scope == "global"):
				self.context.addGlobal (paramParts[0],result)
			else:
				self.hasLocals = 1
				localsList.append ((paramParts[0], result))
		if (self.hasLocals):
			self.context.addLocals (localsList)
		return 0
					
	def handleEndTag (self, tagValue):
		if (self.hasLocals):
			self.context.popLocals()
		
	def getPriority (self):
		return 1
		
class TALException:
	def __init__ (self, txt):
		self.txt = txt
		
	def __str__ (self):
		return self.txt.encode ('ascii', 'replace')
		
class EventRecorder:
	# We use copy.deepcopy to keep list of attributes intact
	def __init__ (self, startTagVal):
		self.eventQueue = []
		self.recordStart (startTagVal.getTag(), startTagVal.getAttributes())
		
	def recordStart (self, tag, attributes):
		self.eventQueue.append (('start', tag, copy.deepcopy (attributes)))
		
	def recordEnd (self, tag):
		self.eventQueue.append (('end', tag))
		
	def recordData (self, data):
		self.eventQueue.append (('data', data))
	
	def playBack (self, handler):
		handler.suspendRecord()
		for event in self.eventQueue:
			if (event[0] == 'start'):
				handler.unknown_starttag (event[1], copy.deepcopy (event[2]))
			elif (event[0] == 'end'):
				handler.unknown_endtag (event[1])
			elif (event[0] == 'data'):
				handler.handle_data (event[1])
		handler.enableRecord()
		
class HTMLParser (sgmllib.SGMLParser):
	def setupParser (self, context, output, encoding, allowTALInStructure):
		self.log = logging.getLogger ("simpleTAL.HTMLParser")
		self.eventHandler = EventHandler (context, output, self.parseStructure)
		self.encoding = encoding
		self.allowTALInStructure = allowTALInStructure
		
	def parseStructure (self, structure):
		# Called when evaluating a structure
		self.log.debug ("Creating child parser to read structure.")
		newParser = HTMLParser ()
		newParser.log = logging.getLogger ("simpleTAL.HTMLParser.Child")
		newParser.eventHandler = self.eventHandler
		# Any data sent into this new version will already be in unicode!
		newParser.encoding = None
		
		# Inform the event handler whether TAL attributes should be used or ignored
		if (not self.allowTALInStructure):
			self.eventHandler.enableTALHandling (0)
		self.log.debug ("Feeding structure to child parser")
		newParser.feed (structure)
		newParser.close()
		
		# Turn TAL handling back on if we turned it off.
		if (not self.allowTALInStructure):
			self.eventHandler.enableTALHandling (1)
		self.log.debug ("Finished with child parser - returning.")
		
	def unknown_starttag (self, tag, attributes):
		self.log.debug ("Recieved Real Start Tag: " + tag + " Attributes: " + str (attributes))
		if (self.encoding is None):
			# If we have no encoding it means that we are recieving unicode already
			self.eventHandler.unknown_starttag (tag, attributes)
		else:
			# Unicode the data
			atts = []
			for at in attributes:
				atts.append ((unicode (at[0], self.encoding), unicode (at[1], self.encoding)))
			self.eventHandler.unknown_starttag (unicode (tag, self.encoding), atts)
		
	def unknown_endtag (self, tag):
		self.log.debug ("Recieved Real End Tag: " + tag)
		if (self.encoding is None):
			self.eventHandler.unknown_endtag (tag)
		else:
			self.eventHandler.unknown_endtag (unicode (tag, self.encoding))
			
	def handle_data (self, data):
		self.log.debug ("Recieved Real Data: " + data)
		if (self.encoding is None):
			self.eventHandler.handle_data (data)
		else:
			self.eventHandler.handle_data (unicode (data, self.encoding))
			
class XMLParser (xml.sax.handler.ContentHandler):
	def setupParser (self, context, output, allowTALInStructure):
		self.log = logging.getLogger ("simpleTAL.XMLParser")
		self.eventHandler = EventHandler (context, output, self.parseStructure)
		self.allowTALInStructure = allowTALInStructure
		
	def parseStructure (self, structure):
		# Called when evaluating a structure
		self.log.debug ("Creating child XML Parser for structure.")
		newParser = XMLParser()
		newParser.log = logging.getLogger ("simpleTAL.XMLParser.Child")
		newParser.eventHandler = self.eventHandler
		structureFile = StringIO.StringIO (structure)
		
		# Inform the event handler whether TAL attributes should be used or ignored
		if (not self.allowTALInStructure):
			self.eventHandler.enableTALHandling (0)
			
		self.log.debug ("Parsing structure with child.")
		xml.sax.parse (structureFile, newParser)
		
		# # Turn TAL handling back on if we turned it off.
		if (not self.allowTALInStructure):
			self.eventHandler.enableTALHandling (1)
			
		self.log.debug ("Finished, returning.")
		
	def startElement (self, tag, attributes):
		self.log.debug ("Recieved Real Start Tag: " + tag + " Attributes: " + str (attributes))
		# Convert attributes into a list of tuples
		atts = []
		for att in attributes.keys():
			atts.append ((att, attributes [att]))
		self.eventHandler.unknown_starttag (tag, atts)
		
	def endElement (self, tag):
		self.log.debug ("Recieved Real End Tag: " + tag)
		self.eventHandler.unknown_endtag (tag)
			
	def characters (self, data):
		self.log.debug ("Recieved Real Data: " + data)
		self.eventHandler.handle_data (data)
	
class EventHandler:
	def __init__ (self, context, output, structureParser):
		self.log = logging.getLogger ("simpleTAL.EventHandler")
		self.context = context
		self.output = output
		self.structureParser = structureParser
		
		self.elementStack = ElementStack ()

		# When playing back recordings we need to suppress all further recordings
		# up the tree - but enable down the tree of recorders.
		self.recordUpperLimitStack = []
		self.recorderList = []
		self.repeatHook = None
		
		# By default TAL Handling is switched on
		self.enableTALHandling (1)
						  
	def enableTALHandling (self, switchVal):
		if (switchVal):
			# Enable TAL Handling
			self.handlerMap = {'tal:attributes': TALAttribute, 'tal:content': TALContent
						  ,'tal:define': TALDefine, 'tal:replace': TALReplace
						  ,'tal:omit-tag': TALOmitTag, 'tal:condition': TALCondition
						  ,'tal:repeat': TALRepeat}
		else:
			# Disable TAL Handling
			self.handlerMap = {}
						  
	def pushRecorder (self, recorder):
		self.recorderList.append (recorder)
		
	def popRecorder (self, tag):
		oldRecorder = self.recorderList.pop()
		return oldRecorder
	
	def suspendRecord (self):
		# During play back we suspend recording for anything above us in the recorderList
		self.recordUpperLimitStack.append (len (self.recorderList))
		
	def enableRecord (self):
		# After play back we re-enable the recording for our parents
		self.recordUpperLimitStack.pop()
	
	def getActiveRecorders (self):
		# Return a list of recorder that are active
		if (len (self.recordUpperLimitStack) == 0):
			return self.recorderList
		else:
			limit = self.recordUpperLimitStack[-1:][0]	
			return self.recorderList[limit:]
			
	def setRepeatHook (self, func):
		self.repeatHook = func
		
	def clearRepeatHook (self):
		self.repeatHook = None
		
	def getContext (self):
		return self.context
		
	def parseStructure (self, structure):
		# When parsing a structure disable recording for parents
		self.suspendRecord()
		self.structureParser (structure)
		self.enableRecord()
		
	def unknown_starttag (self, tag, attributes):
		self.log.debug ("Start Tag: " + tag + " Attributes: " + str (attributes))
					
		for recorder in self.getActiveRecorders():
			recorder.recordStart (tag, attributes)
			
		if (self.output.suppress()):
			self.log.debug ("Suppression turned on - suppressing: " + tag)
			# Still suppressing - we don't output anything
			self.output.pushSuppressionTag (tag)
			return
				
		handlerList = []
		for att in attributes:
			if self.handlerMap.has_key (att[0]):
				handler = apply (self.handlerMap.get (att[0]), (att[1], self))
				self.log.debug ("Created handler: " + str (handler))
				handlerList.append (handler)
		if (len (handlerList) == 0):
			# We need a default handler
			handlerList.append (TALHandler (None, self))
		handlerList.sort()
		
		# Create tag value and then pass to each handler
		tagVal = TagValue (tag, attributes)
		for handler in handlerList:
			if (handler.handleStartTag (tagVal)):
				# Someone in here wants to suppress - let's do it!
				self.output.pushSuppressionTag (tag)
				return
		
		self.elementStack.push (tagVal, handlerList)
		
		# Now see if this should be output
		if (tagVal.getTagEnabled()):
			self.output.startElement (tag, attributes)
			
	def handle_data (self, data):
		for recorder in self.getActiveRecorders():
			recorder.recordData (data)
			
		if (self.output.suppress()):
			self.log.debug ("Suppressing data: " + data)
			return
			
		curTag = self.elementStack.getCurrentTagValue()
		self.log.debug ("CurTag: " + str (curTag))
		if (curTag is not None and curTag.getContentEnabled()):
			self.output.characters (data)
				
	def unknown_endtag (self, tag):
		self.log.debug ("End Tag: " + tag)
		for recorder in self.getActiveRecorders():
			recorder.recordEnd (tag)
							
		if (self.output.suppress()):
			self.output.popSuppressionTag(tag)
			# We were still suppressing
			return
		
		# Get the handler list
		next = self.elementStack.pop(tag)
		if (next is None):
			self.log.warn ("Warning - close tag for document not found!")
			return
			
		tagVal, handlerList = next
		for handler in handlerList:
			handler.handleEndTag (tagVal)
			
		self.output.characters (tagVal.getOverrideCharacters())
		if tagVal.getTagEnabled():
			self.output.endElement (tag)
			
		# If there is a repeat hook function - call it!
		if (self.repeatHook is not None):
			apply (self.repeatHook, ())

def expandTemplate (file, context, inputEncoding="iso8859-1"
									 ,outputEncoding="iso8859-1", allowTALInStructure=1):
	output = HTMLOuput(outputEncoding)
	parser = HTMLParser()
	parser.setupParser (context, output, inputEncoding, allowTALInStructure)
	parser.feed (file.read())
	parser.close()
	return output.getValue()
	
def expandXMLTemplate (file, context, outputEncoding="iso8859-1", allowTALInStructure=1):
	stringFile = StringIO.StringIO()
	output = XMLOutput(stringFile, outputEncoding)
	
	handler = XMLParser()
	handler.setupParser (context, output, allowTALInStructure)
	
	xml.sax.parse (file, handler)
	return stringFile.getvalue()
			
#talTest = TAL ()
#talTest.parse (open ("test.html"))


