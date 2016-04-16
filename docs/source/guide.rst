TAL/TALES and METAL Reference Guide
###################################

A guide to using TAL_, TALES_, and METAL_.

Introduction
============

This is a simple reference guide to the TAL and TALES languages.  Formal language specifications are hosted by Zope: TAL_ , TALES_ , METAL_ .

.. _TAL: https://web.archive.org/web/20130517091955/http://wiki.zope.org/ZPT/TAL
.. _TALES: https://web.archive.org/web/20130517091955/http://wiki.zope.org/ZPT/TAL
.. _METAL: https://web.archive.org/web/20130517091955/http://wiki.zope.org/ZPT/TAL

.. highlight:: html

TAL Commands
============

TAL_ consists of seven different commands (highest priority first):

    * `tal:define`_
    * `tal:condition`_
    * `tal:repeat`_
    * `tal:content`_
    * `tal:replace`_
    * `tal:attributes`_
    * `tal:omit-tag`_

Commands are attributes on HTML or XML tags, e.g. ``<div tal:content="article">Article goes here</div>``

tal:define
----------

Syntax: ``tal:define="[local | global] name expression [; define-expression...]"``

Description: Sets the value of "name" to "expression".  By default the name will be applicable in the "local" scope, which consists of this tag, and all other tags nested inside this tag.  If the "global" keyword is used then this name will keep its value for the rest of the document.

Example::

    <div tal:define="global title book/theTitle; local chapterTitle book/chapter/theTitle">

tal:condition
-------------

Syntax: ``tal:condition="expression"``

Description:  If the expression evaluates to true then this tag and all its children will be output.  If the expression evaluates to false then this tag and all its children will not be included in the output.

Example::

    <h1 tal:condition="user/firstLogin">Welcome to this page!</h1>


tal:repeat
----------

Syntax: ``tal:repeat="name expression"``

Description:  Evaluates "expression", and if it is a sequence, repeats this tag and all children once for each item in the sequence.  The "name" will be set to the value of the item in the current iteration, and is also the name of the repeat variable.  The repeat variable is accessible using the TAL path: repeat/name and has the following properties:

   * index - Iteration number starting from zero

   * number - Iteration number starting from one

   * even - True if this is an even iteration

   * odd - True if this is an odd iteration

   * start - True if this is the first item in the sequence

   * end - True if this is the last item in the sequence.  For iterators this is never true

   * length - The length of the sequence.  For iterators this is maxint as the length of an iterator is unknown

   * letter - The lower case letter for this iteration, starting at "a"

   * Letter - Upper case version of letter

   * roman - Iteration number in Roman numerals, starting at i

   * Roman - Upper case version of roman

Example::

    <table>
      <tr tal:repeat="fruit basket">
        <td tal:content="repeat/fruit/number"></td>
        <td tal:content="fruit/name"></td>
      </tr>
    </table>



tal:content
-----------

Syntax: ``tal:content="[text | structure] expression"``

Description:  Replaces the contents of the tag with the value of "expression".  By default, and if the "text" keyword is present, then the value of the expression will be escaped as required (i.e. characters "&<> will be escaped).  If the "structure" keyword is present then the value will be output with no escaping performed.

Example::

    <h1 tal:content="user/firstName"></h1>

tal:replace
-----------

Syntax: ``tal:replace="[text | structure] expression"``

Description: Behaves identically to tal:content, except that the tag is removed from the output (as if tal:omit-tag had been used).

Example::

    <h1>Welcome <b tal:replace="user/firstName"></b></h1>

tal:attributes
--------------

Syntax: ``tal:attributes="name expression[;attributes-expression]"``

Description:  Evaluates each "expression" and replaces the tag's attribute "name".  If the expression evaluates to nothing then the attribute is removed from the tag.  If the expression evaluates to default then the original tag's attribute is kept.  If the "expression" requires a semi-colon then it must be escaped by using ";;".

Example::

    <a tal:attributes="href user/homepage;title user/fullname">Your Homepage</a>
    

tal:omit-tag
------------

Syntax: ``tal:omit-tag="expression"``

Description: Removes the tag (leaving the tags content) if the expression evaluates to true.  If expression is empty then it is taken as true.

Example::

    <h1>
      <b tal:omit-tag="not:user/firstVisit">Welcome</b> to this page!
    </h1>

TALES Expressions
=================

The expressions used in TAL_ are called TALES_ expressions.  The simplest TALES_ expression is a path which references a value, e.g. page/body references the body property of the page object.

path
----

Syntax: ``[path:]string[|TALES Expression]``

Description: A path, optionally starting with the modifier 'path:', references a property of an object.  The '/' delimiter is used to end the name of an object and the start of the property name.  Properties themselves may be objects that in turn have properties.  The '|' ("or") character is used to find an alternative value to a path if the first path evaluates to 'Nothing' or does not exist.

Example::

    <p tal:content="book/chapter/title | string:Untitled"></p>

There are several built in paths that can be used in paths:

   * nothing - acts as None in Python

   * default - keeps the existing value of the node (tag content or attribute value)

   * options - the dictionary of values passed to the template (through the Context __init__ method)

   * repeat - access the current repeat variable (see tal:repeat)

   * attrs - a dictionary of original attributes of the current tag

   * CONTEXTS - a dictionary containing all of the above

exists
------

Syntax: ``exists:path``

Description: Returns true if the path exists, false otherwise.  This is particularly useful for removing tags from output when the tags will have no content.

Example::

    <p tal:omit-tag="not:exists:book/chapter/title" tal:content="book/chapter/title"></p>

nocall
------

Syntax: ``nocall:path``

Description: Returns a reference to a path, but without evaluating the path. Useful when you wish to define a new name to reference a function, not the current value of a function.

Example::

    <p tal:define="title nocall:titleFunction" tal:content="title"></p>

not
---

Syntax: ``not:tales-path``

Description: Returns the inverse of the tales-path.  If the path returns true, ``not:path`` will return false.

Example::

    <p tal:condition="not: user/firstLogin">Welcome to the site!</p>

string
------

Syntax: ``string:text``

Description:  Evaluates to a literal string with value text while substituting variables with the form ``${pathName}`` and ``$pathName``

Example::

    <b tal:content="string:Welcome ${user/name}!"></b>

python
------

Syntax: ``python:python-code``

Description:  Evaluates the python-code and returns the result.  The python code must be properly escaped, e.g. "python: 1 < 2" must be written as "python: 1 &lt; 2".  The python code has access to all Python functions, including four extra functions that correspond to their TALES commands: path (string), string (string), exists (string), and nocall (string)

Example::

    <div tal:condition="python: path (basket/items) &gt; 1">Checkout!</div>

METAL Macro Language
====================

METAL_ is a macro language commonly used with TAL_ and TALES_.  METAL_ allows part of a template to be used as a macro in later parts of a template, or a separate template altogether.

metal:define-macro
------------------

Syntax: ``metal:define-macro="name"``

Description:  Defines a new macro that can be reference later as "name".

Example::

    <div metal:define-macro="footer">
      Copyright <span tal:content="page/lastModified">2004</span>
    </div>

metal:use-macro
---------------

Syntax: ``metal:use-macro="expression"``

Description:  Evaluates "expression" and uses this as a macro.

Example::

    <div metal:use-macro="footer"></div>

metal:define-slot
-----------------

Syntax: ``metal:define-slot="name"``

Description:  Defines a customisation point in a macro with the given name.

Example::

    <div metal:define-macro="footer">
      <b>Standard disclaimer for the site.</b>
      <i metal:define-slot="Contact">Contact admin@site.com</i>
    </div>

metal:fill-slot
---------------

Syntax: ``metal:fill-slot="name"``

Description:  Replaces the content of a slot with this element.

Example::

    <div metal:use-macro="footer">
      <i metal:fill-slot="Contact">Contact someone else</i>
    </div>