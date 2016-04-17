# -*- coding: iso-8859-1 -*-

#    Copyright (c) 2016, Jan Brohl <janbrohl@t-online.de>
#    All rights reserved.
#    See LICENSE.txt

#    Copyright (c) 2005 Colin Stewart (http://www.owlfish.com/)
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions
#    are met:
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. The name of the author may not be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
#    IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#    OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#    IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
#    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#    NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
#    THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#    If you make any bug fixes or feature enhancements please let me know!

""" simpleTALUtils
		
		This module is holds utilities that make using SimpleTAL easier. 
		Initially this is just the HTMLStructureCleaner class, used to clean
		up HTML that can then be used as 'structure' content.
		
"""

from __future__ import absolute_import

import os.path
import os
import stat
import threading
import sys
import codecs
import cgi
import re
import xml.sax
import xml.sax.handler
import io
import simpletal.simpleTAL
import simpletal.simpleTALES
import simpletal.simpleTALConstants

# used to check if a path points to an HTML-file
HTML_EXT_REGEX = re.compile(".*[.]html?$", re.IGNORECASE)

# used to check quite strictly that a name does not have a special meaning
# for the filesystem
SAFE_NAME_REGEX = re.compile("(?:[a-zA-Z0-9]+[_-]+)*[a-zA-Z0-9]+$")


class TemplateCache(object):
    """ A TemplateCache is a multi-thread safe object that caches compiled templates.
                    This cache only works with file based templates, the ctime of the file is 
                    checked on each hit, if the file has changed the template is re-compiled.
    """

    def __init__(self):
        self.templateCache = {}
        self.cacheLock = threading.Lock()
        # debugging info
        self.hits = 0
        self.misses = 0

    def isHTML(self, name):
        return HTML_EXT_REGEX.match(name) is not None

    def getTemplate(self, name, inputEncoding='UTF-8-SIG'):
        """ Name should be the path of a template file.  If self.isHTML(name) it is treated
                as an HTML Template, otherwise it's treated as an XML Template.  If the template file
                has changed since the last cache it will be re-compiled.

                inputEncoding is only used for HTML templates, and should be the encoding that the template
                is stored in.
        """
        return self._cacheTemplate_(name, inputEncoding)

    def getXMLTemplate(self, name):
        """ Name should be the path of an XML template file.  
        """
        return self._cacheTemplate_(name, None, xmlTemplate=1)

    def _cacheTemplate_(self, name, inputEncoding, xmlTemplate=0):
        with self.cacheLock:
            template, oldmtime = self.templateCache.get(name, (None, None))
            mtime = os.path.getmtime(name)
            if template is not None:
                if (oldmtime == mtime):
                    # Cache hit!
                    self.hits += 1
                    return template

            # Cache miss, let's cache this template
            with open(name, 'r') as tempFile:
                if (xmlTemplate):
                    # We know it is XML
                    template = simpletal.simpleTAL.compileXMLTemplate(tempFile)
                else:
                    # We have to guess...
                    if self.isHTML(name):
                        template = simpletal.simpleTAL.compileHTMLTemplate(
                            tempFile, inputEncoding)
                    else:
                        template = simpletal.simpleTAL.compileXMLTemplate(
                            tempFile)
                self.templateCache[name] = (
                    template, mtime)
                self.misses += 1
            return template


class TemplateFolder(object):  # TODO: write tests, docs, find better name

    def __init__(self, root, getfunc, ext=".html", path=tuple()):
        self._ext = ext
        self._root = root
        self._getfunc = getfunc
        self._path = path

    def __getattr__(self, name):
        if SAFE_NAME_REGEX.match(name) is None:
            raise AttributeError("%r is not allowed" % name)
        if name == "container" and self._path:
            return self.__class__(self._root, self._getfunc, self._ext, self._path[:-1])
        newPath = self._path + (name,)
        fullPath = os.path.join(self._root, *newPath)
        if os.path.isdir(fullPath):
            return self.__class__(self._root, self._getfunc, self._ext, newPath)
        elif os.path.isfile(fullPath + self._ext):
            return self._getfunc(fullPath + self._ext)
        else:
            raise AttributeError(name)

    def __iter__(self):
        e = self._ext
        le = len(e)
        for name in sorted(os.listdir(os.path.join(self._root, *self._path))):
            if name.endswith(e):
                n = name[:-le]
                if SAFE_NAME_REGEX.match(n):
                    yield n
            elif SAFE_NAME_REGEX.match(name):
                yield name


class TemplateWrapper(object):  # TODO: write tests, docs, find better name

    def __init__(self, template, contextGlobals={}, allowPythonPath=False):
        self.template = template
        self.contextGlobals = contextGlobals
        self.allowPythonPath = allowPythonPath

    def __call__(self, func):
        return (lambda *args, **kwargs: self.expand(func(*args, **kwargs)))

    def _ctx(self, options, updateGlobals, kwGlobals):
        g = self.contextGlobals.copy()
        g.update(updateGlobals)
        g.update(kwGlobals)
        ctx = simpletal.simpleTALES.Context(options, self.allowPythonPath)
        for k, v in g.items():
            ctx.addGlobal(k, v)
        return ctx

    def expand(self, options=tuple(), updateGlobals={}, **kwGlobals):
        ctx = self._ctx(options, updateGlobals, kwGlobals)
        f = io.StringIO()
        self.template.expand(ctx, f)
        return f.getvalue()

    def expandMacros(options=tuple(), updateGlobals={}, **kwGlobals):
        ctx = self._ctx(options, updateGlobals, kwGlobals)
        f = io.StringIO()
        expandMacros(ctx, self.template)
        return f.getvalue()


# TODO: write tests, docs, find better name
def wrapperLoader(templateDir="templates", standardGlobals={}):
    cache = TemplateCache()
    root = TemplateFolder(templateDir, cache.getTemplate)
    standardGlobals = standardGlobals.copy()
    standardGlobals["root"] = root

    def load(path):
        pathtuple = tuple(path.strip("/").split("/"))
        container = TemplateFolder(
            templateDir, cache.getTemplate, path=pathtuple[:-1])
        contextGlobals = standardGlobals.copy()
        contextGlobals["container"] = container
        loader = TemplateFolder(templateDir, (lambda name: TemplateWrapper(
            cache.getTemplate(name), contextGlobals)), path=pathtuple[:-1])
        return getattr(loader, pathtuple[-1])

    return load


class MacroExpansionInterpreter (simpletal.simpleTAL.TemplateInterpreter):

    def __init__(self):
        simpletal.simpleTAL.TemplateInterpreter.__init__(self)
        # Override the standard interpreter way of doing things.
        self.macroStateStack = []
        self.commandHandler.update({simpletal.simpleTALConstants.TAL_DEFINE: self.cmdNoOp,
                                    simpletal.simpleTALConstants.TAL_CONDITION: self.cmdNoOp,
                                    simpletal.simpleTALConstants.TAL_REPEAT: self.cmdNoOp,
                                    simpletal.simpleTALConstants.TAL_CONTENT: self.cmdNoOp,
                                    simpletal.simpleTALConstants.TAL_ATTRIBUTES: self.cmdNoOp,
                                    simpletal.simpleTALConstants.TAL_OMITTAG: self.cmdNoOp,
                                    simpletal.simpleTALConstants.TAL_START_SCOPE: self.cmdStartScope,
                                    simpletal.simpleTALConstants.TAL_OUTPUT: self.cmdOutput,
                                    simpletal.simpleTALConstants.TAL_STARTTAG: self.cmdOutputStartTag,
                                    simpletal.simpleTALConstants.TAL_ENDTAG_ENDSCOPE: self.cmdEndTagEndScope,
                                    simpletal.simpleTALConstants.METAL_USE_MACRO: self.cmdUseMacro,
                                    simpletal.simpleTALConstants.METAL_DEFINE_SLOT: self.cmdDefineSlot,
                                    simpletal.simpleTALConstants.TAL_NOOP: self.cmdNoOp})

        self.inMacro = None
        self.macroArg = None
    # Original cmdOutput
    # Original cmdEndTagEndScope

    def popProgram(self):
        self.inMacro = self.macroStateStack.pop()
        simpletal.simpleTAL.TemplateInterpreter.popProgram(self)

    def pushProgram(self):
        self.macroStateStack.append(self.inMacro)
        simpletal.simpleTAL.TemplateInterpreter.pushProgram(self)

    def cmdOutputStartTag(self, command, args):
        newAtts = []
        for att, value in self.originalAttributes.items():
            if (self.macroArg is not None and att == "metal:define-macro"):
                newAtts.append(("metal:use-macro", self.macroArg))
            elif (self.inMacro and att == "metal:define-slot"):
                newAtts.append(("metal:fill-slot", value))
            else:
                newAtts.append((att, value))
        self.macroArg = None
        self.currentAttributes = newAtts
        simpletal.simpleTAL.TemplateInterpreter.cmdOutputStartTag(
            self, command, args)

    def cmdUseMacro(self, command, args):
        simpletal.simpleTAL.TemplateInterpreter.cmdUseMacro(
            self, command, args)
        if (self.tagContent is not None):
            # We have a macro, add the args to the in-macro list
            self.inMacro = 1
            self.macroArg = args[0]

    def cmdEndTagEndScope(self, command, args):
        # Args: tagName, omitFlag
        if (self.tagContent is not None):
            contentType, resultVal = self.tagContent
            if (contentType):
                if (isinstance(resultVal, simpletal.simpleTAL.Template)):
                    # We have another template in the context, evaluate it!
                    # Save our state!
                    self.pushProgram()
                    resultVal.expandInline(self.context, self.file, self)
                    # Restore state
                    self.popProgram()
                    # End of the macro expansion (if any) so clear the
                    # parameters
                    self.slotParameters = {}
                    # End of the macro
                    self.inMacro = 0
                else:
                    if (isinstance(resultVal, unicode)):
                        self.file.write(resultVal)
                    elif (isinstance(resultVal, str)):
                        self.file.write(unicode(resultVal, 'ascii'))
                    else:
                        self.file.write(unicode(str(resultVal), 'ascii'))
            else:
                if (isinstance(resultVal, unicode)):
                    self.file.write(cgi.escape(resultVal))
                elif (isinstance(resultVal, str)):
                    self.file.write(cgi.escape(unicode(resultVal, 'ascii')))
                else:
                    self.file.write(cgi.escape(
                        unicode(str(resultVal), 'ascii')))

        if (self.outputTag and not args[1]):
            self.file.write('</' + args[0] + '>')

        if (self.movePCBack is not None):
            self.programCounter = self.movePCBack
            return

        if (self.localVarsDefined):
            self.context.popLocals()

        (self.movePCForward, self.movePCBack, self.outputTag,
         self.originalAttributes, self.currentAttributes, self.repeatVariable,
         self.tagContent, self.localVarsDefined) = self.scopeStack.pop()
        self.programCounter += 1


def expandMacros(context, template, outputFile, outputEncoding="utf-8"):
    """
        This function can be used to expand a template which contains METAL 
        macros, while leaving in place all the TAL and METAL commands.

        Doing this makes editing a template which uses METAL macros easier, 
        because the results of the macro can be seen immediately.
        The macros referred to by the passed in template must be present in 
        the context so that their contents can be referenced.  The 
        outputEncoding determines the encoding of the returned string, which 
        will contain the expanded macro.
    """
    interp = MacroExpansionInterpreter()
    interp.initialise(context, outputFile)
    return template.expand(context, outputFile, outputEncoding, interpreter=interp)


def ExpandMacros(context, template, outputEncoding="utf-8"):
    f = io.BytesIO()
    expandMacros(context, template, f, outputEncoding)
    return f.getvalue()
