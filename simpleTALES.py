""" simpleTALES Implementation

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial
		use.  No warranties, expressed or implied, are made as to the
		fitness of this code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		The classes in this module implement the TALES specification, used
		by the simpleTAL module.
		
		Module Dependencies: logging
"""

__version__ = "3.0"

import copy, string

try:
	import logging
except:
	import DummyLogger as logging


class ContextVariable:
	def __init__ (self, value = None):
		self.ourValue = value
		
	def isDefault (self):
		return 0
		
	def isNothing (self):
		if (self.value() is None):
			return 1
		return 0
		
	def isSequence (self):
		# Return the length of the sequence - if it's zero length then it's handled
		# as though it wasn't a sequence at all.
		try:
			seqLength = len (self.value())
			temp = self.value()[1:1]
			return seqLength
		except:
			return 0
		
	def isCallable (self):
		return callable (self.ourValue)
		
	def isTrue (self):
		if (self.isNothing()):
			return 0
		if (self.isDefault()):
			return 1
		if (self.isSequence()):
			return len (self.value())
		return self.value()
		
	def value (self):
		if (callable (self.ourValue)):
			return apply (self.ourValue, ())
		return self.ourValue
		
	def __str__ (self):
		return 
		try:
			return str (self.ourValue)
		except UnicodeError, e:
			# Ignore - just return the value decoded
			return self.ourValue.encode ('ASCII', 'replace')
		
class DefaultVariable (ContextVariable):
	def __init__ (self):
		ContextVariable.__init__ (self, 1)
		
	def isNothing (self):
		return 0
		
	def isDefault (self):
		return 1
		
	def value (self):
		# We return our self so that define works properly.
		return self
		
	def __str__ (self):
		return "Default"
		
class NothingVariable (ContextVariable):
	def __init__ (self):
		ContextVariable.__init__ (self, None)
				
	def isNothing (self):
		return 1
		
class NoCallVariable (ContextVariable):
	def __init__ (self, variable):
		ContextVariable.__init__ (self, variable.ourValue)
		self.variable = variable
		
	def value (self):
		return self.ourValue
		
class RepeatVariable (ContextVariable):
	""" To be written"""
	def __init__ (self, sequence):
		ContextVariable.__init__ (self, 1)
		self.sequence = sequence	
		self.position = 0	
		self.map = None
		
	def value (self):
		if (self.map is None):
			self.createMap()
		return self.map
		
	def increment (self):
		self.position += 1
		
	def createMap (self):
		self.map = {}
		self.map ['index'] = self.getIndex
		self.map ['number'] = self.getNumber
		self.map ['even'] = self.getEven
		self.map ['odd'] = self.getOdd
		self.map ['start'] = self.getStart
		self.map ['end'] = self.getEnd
		# TODO: first and last need to be implemented.
		self.map ['length'] = len (self.sequence)
		self.map ['letter'] = self.getLowerLetter
		self.map ['Letter'] = self.getUpperLetter
		self.map ['roman'] = self.getLowerRoman
		self.map ['Roman'] = self.getUpperRoman
	
	# Repeat implementation goes here
	def getIndex (self):
		return self.position
		
	def getNumber (self):
		return self.position + 1
		
	def getEven (self):
		if ((self.position % 2) != 0):
			return 0
		return 1
		
	def getOdd (self):
		if ((self.position % 2) == 0):
			return 0
		return 1
		
	def getStart (self):
		if (self.position == 0):
			return 1
		return 0
		
	def getEnd (self):
		if (self.position == len (self.sequence) - 1):
			return 1
		return 0
		
	def getLowerLetter (self):
		result = ""
		nextCol = self.position
		if (nextCol == 0):
			return 'a'
		while (nextCol > 0):
			nextCol, thisCol = divmod (nextCol, 26)
			result = chr (ord ('a') + thisCol) + result
		return result
	
	def getUpperLetter (self):
		return string.upper (self.getLowerLetter())
		
	def getLowerRoman (self):
		romanNumeralList = (('m', 1000)
						   ,('cm', 900)
						   ,('d', 500)
						   ,('cd', 400)
						   ,('c', 100)
						   ,('xc', 90)
						   ,('l', 50)
						   ,('xl', 40)
						   ,('x', 10)
						   ,('ix', 9)
						   ,('v', 5)
						   ,('iv', 4)
						   ,('i', 1)
						   )
		if (self.position > 3999):
			# Roman numbers only supported up to 4000
			return ' '
		num = self.position + 1
		result = ""
		for roman, integer in romanNumeralList:
			while (num >= integer):
				result += roman
				num -= integer
		return result
		
	def getUpperRoman (self):
		return string.upper (self.getLowerRoman())
		
				
class Context:
	def __init__ (self, options=None):
		self.globals = {}
		self.locals = {}
		self.localStack = []
		self.populateDefaultVariables (options)
		self.log = logging.getLogger ("simpleTALES.Context")
		self.true = ContextVariable (1)
		self.false = ContextVariable (0)
		
	def addRepeat (self, name, var):
		self.repeatMap [name] = var
		
	def removeRepeat (self, name):
		del self.repeatMap [name]
		
	def addGlobal (self, name, value):
		if (isinstance (value, ContextVariable)):
			self.globals[name] = value
		else:
			self.globals[name] = ContextVariable (value)
		
	def addLocals (self, localVarList):
		# Pop the current locals onto the stack
		self.localStack.append (self.locals)
		self.locals = copy.copy (self.locals)
		for var in localVarList:
			name, value = var
			if (isinstance (value, ContextVariable)):
				self.locals [name] = value
			else:
				self.locals [name] = ContextVariable (value)
				
	def setLocal (self, name, value):
		# Override the current local if present with the new one
		if (isinstance (value, ContextVariable)):
			self.locals [name] = value
		else:
			self.locals [name] = ContextVariable (value)
		
	def popLocals (self):
		self.locals = self.localStack.pop()
		
	def evaluate (self, expr, originalAtts = None):
		# Returns a ContextVariable
		self.log.debug ("Evaluating %s" % expr)
		if (originalAtts is not None):
			# Call from outside
			self.globals['attrs'] = ContextVariable(originalAtts)
			# Check for an correct for trailing/leading quotes
			if (expr[0] == '"' or expr[0] == "'"):
				expr = expr [1:]
			if (expr[-1] == '"' or expr[-1] == "'"):
				expr = expr [0:-1]
			
		# Supports path, exists, nocall, not, and string
		expr = string.strip(expr)
		if (expr[0:5] == 'path:'):
			return self.evaluatePath (string.strip (expr[5:]))
		elif (expr[0:7] == 'exists:'):
			return self.evaluateExists (string.strip (expr[7:]))
		elif (expr[0:7] == 'nocall:'):
			return self.evaluateNoCall (string.strip (expr[7:]))
		elif (expr[0:4] == 'not:'):
			return self.evaluateNot (string.strip (expr[4:]))
		elif (expr[0:7] == 'string:'):
			return self.evaluateString (string.strip (expr[7:]))
		else:
			# Not specified - so it's a path
			return self.evaluatePath (expr)
		
	def evaluatePath (self, expr):
		self.log.debug ("Evaluating path expression %s" % expr)
		allPaths = expr.split ('|')
		if (len (allPaths) > 1):
			for path in allPaths:
				# Evaluate this path
				pathResult = self.evaluate (string.strip (path))
				if (pathResult is not None):
					return pathResult
			return None
		else:
			# A single path - so let's evaluate it
			return self.traversePath (allPaths[0])
			
	def evaluateExists (self, expr):
		self.log.debug ("Evaluating %s to see if it exists" % expr)
		allPaths = expr.split ('|')
		if (len (allPaths) > 1):
			# The first path is for us
			# Return true if this first bit evaluates, otherwise test the rest
			result = self.traversePath (allPaths[0])
			if (result is not None):
				return self.true
			
			for path in allPaths[1:]:
				# Evaluate this path
				pathResult = self.evaluate (string.strip (path))
				if (pathResult is not None):
					return self.true
			return None
		else:
			# A single path - so let's evaluate it
			result =  self.traversePath (allPaths[0])
			if (result is None):
				return None
			return self.true
			
	def evaluateNoCall (self, expr):
		self.log.debug ("Evaluating %s using nocall" % expr)
		allPaths = expr.split ('|')
		if (len (allPaths) > 1):
			# The first path is for us
			result = self.traversePath (allPaths[0], canCall = 0)
			if (result is not None):
				return result
				
			for path in allPaths[1:]:
				# Evaluate this path
				pathResult = self.evaluate (string.strip (path))
				if (pathResult is not None):
					return pathResult
			return None
		else:
			# A single path - so let's evaluate it
			return self.traversePath (allPaths[0], canCall=0)
			
	def evaluateNot (self, expr):
		self.log.debug ("Evaluating NOT value of %s" % expr)
		
		# Evaluate what I was passed
		pathResult = self.evaluate (expr)
		if (pathResult is None):
			# None of these paths exist!
			return self.true
		if (pathResult.isTrue()):
			return self.false
		return self.true
		
	def evaluateString (self, expr):
		self.log.debug ("Evaluating String %s" % expr)
		result = ""
		skipCount = 0
		for position in xrange (0,len (expr)):
			if (skipCount > 0):
				skipCount -= 1
			else:
				if (expr[position] == '$'):
					try:
						if (expr[position + 1] == '$'):
							# Escaped $ sign
							result += '$'
							skipCount = 1
						elif (expr[position + 1] == '{'):
							# Looking for a path!
							endPos = expr.find ('}', position + 1)
							if (endPos > 0):
								path = expr[position + 2:endPos]
								# Evaluate the path
								pathResult = self.evaluate (path)
								if (pathResult is not None and not pathResult.isNothing()):
									result += pathResult.value()
								skipCount = endPos - position 
						else:
							# It's a variable
							endPos = expr.find (' ', position + 1)
							if (endPos == -1):
								endPos = len (expr)
							path = expr [position + 1:endPos]
							# Evaluate the variable
							pathResult = self.traversePath (path)
							if (pathResult is not None and not pathResult.isNothing()):
								result += pathResult.value()
							skipCount = endPos - position - 1
					except:
						# Trailing $ sign - just suppress it
						self.log.warn ("Trailing $ detected")
						pass
				else:
					result += expr[position]
		return ContextVariable(result)
					
	def traversePath (self, expr, canCall=1):
		self.log.debug ("Traversing path %s" % expr)
		pathList = expr.split ('/')
		path = pathList[0]
		if self.locals.has_key(path):
			val = self.locals[path]
		elif self.globals.has_key(path):
			val = self.globals[path]  
		else:
			# If we can't find it then return None
			return None
		for path in pathList[1:]:
			self.log.debug ("Looking for path element %s" % path)
			if (canCall):
				temp = val.value()
			else:
				temp = NoCallVariable (val).value()
			
			if (hasattr (temp, path)):
				val = getattr (temp, path)
				if (not isinstance (val, ContextVariable)):
					val = ContextVariable (val)
			elif (hasattr (temp, 'has_key')):
				if (temp.has_key (path)):
					val = temp[path]
					if (not isinstance (val, ContextVariable)):
						val = ContextVariable (val)
				else:
					self.log.debug ("Not found.")
					return None		
			else:
				self.log.debug ("Not found.")
				return None
		#self.log.debug ("Found value %s" % str (val))
		if (not canCall):
			return NoCallVariable (val)
		return val
		
	def __str__ (self):
		return "Globals: " + str (self.globals) + "Locals: " + str (self.locals)
		
	def populateDefaultVariables (self, options):
		vars = {}
		self.repeatMap = {}
		self.nothing = NothingVariable()
		vars['nothing'] = self.nothing
		vars['default'] = DefaultVariable()
		vars['options'] = options
		# To start with there are no repeats
		vars['repeat'] = self.repeatMap	
		vars['attrs'] = self.nothing
		
		# Add all of these to the global context
		for name in vars.keys():
			self.addGlobal (name,vars[name])
			
		# Add also under CONTEXTS
		self.addGlobal ('CONTEXTS', vars)

