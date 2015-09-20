""" simpleTALES Implementation

		Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Dummy logging module, used when logging (http://www.red-dove.com/python_logging.html)
		is not installed.
"""

class DummyLogger:
	def debug (self, *args):
		pass
		
	def info (self, *args):
		pass

	def warn (self, *args):
		pass

	def critical (self, *args):
		pass
			
def getLogger (*params):
	return DummyLogger()
	
	
