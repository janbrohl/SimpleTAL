#!/usr/bin/python
""" Copyright 2003 Colin Stewart (http://www.owlfish.com/)
		
		This code is made freely available for commercial and non-commercial use.
		No warranties, expressed or implied, are made as to the fitness of this
		code for any purpose.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""

import unittest, os
import StringIO
import logging, logging.config

from simpletal import simpleTAL, simpleTALES

if (os.path.exists ("logging.ini")):
	logging.config.fileConfig ("logging.ini")
else:
	logging.basicConfig()
	
class TALRepeatTestCases (unittest.TestCase):
	def setUp (self):
		self.context = simpleTALES.Context()
		self.context.addGlobal ('test', 'testing')
		self.context.addGlobal ('one', [1])
		self.context.addGlobal ('two', ["one", "two"])
		self.context.addGlobal ('three', [1,"Two",3])
		self.context.addGlobal ('emptyList', [])
		self.context.addGlobal ('bigList', xrange (1,100))
		self.context.addGlobal ('fourList', ["zero", "one", "two", "three"])
		self.context.addGlobal ('nested', [{'title': 'Image 1', 'catList': [1,2,3]}
												  ,{'title': 'Image 2', 'catList': [5,2,3]}
												  ,{'title': 'Image 3', 'catList': [8,9,1]}
												  ])
		
	def _runTest_ (self, txt, result, errMsg="Error"):
		template = simpleTAL.compileHTMLTemplate (txt)
		file = StringIO.StringIO ()
		try:
			template.expand (self.context, file)
		except Exception, e:
			print "Error, template compiled to: " + str (template)
			raise e
		realResult = file.getvalue()
		self.failUnless (realResult == result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % (errMsg, txt, realResult, result, template))
					
	def testInvalidPath (self):
		self._runTest_ ('<html><p tal:repeat="entry wibble">Hello</p></html>', "<html></html>", "Repeat of non-existant element failed")
		
	def testDefaultValue (self):
		self._runTest_ ('<html><p tal:repeat="entry default">Default Only</p></html>', '<html><p>Default Only</p></html>', 'Default did not keep existing structure intact')
		
	def testStringRepeat (self):
		self._runTest_ ('<html><p tal:omit-tag="" tal:repeat="letter test"><b tal:replace="letter"></b></p></html>', '<html>testing</html>', 'Itteration over string failed.')
	
	def testEmptyList (self):
		self._runTest_ ('<html><p tal:repeat="short emptyList"><b tal:replace="short">Empty</b></p></html>'
									,'<html></html>'
									,'Empty list repeat failed.'
									)
		
	def testListRepeat (self):
		self._runTest_ ('<html><p tal:repeat="word two"><b tal:replace="word"></b></p></html>', '<html><p>one</p><p>two</p></html>', 'Itteration over list failed.')
		
	def testTwoCmndsOneTagListRepeat (self):
		self._runTest_ ('<html><p tal:repeat="word two" tal:content="word"></p></html>'
									 ,'<html><p>one</p><p>two</p></html>'
									 ,'Itteration over list with both content and repeat on same element failed.')
		
	def testNestedRepeat (self):
		self._runTest_ ('<html><p tal:repeat="image nested"><h2 tal:content="image/title"></h2><b tal:omit-tag tal:repeat="category image/catList"><i tal:content="category"></i></b></p></html>'
					   ,'<html><p><h2>Image 1</h2><i>1</i><i>2</i><i>3</i></p><p><h2>Image 2</h2><i>5</i><i>2</i><i>3</i></p><p><h2>Image 3</h2><i>8</i><i>9</i><i>1</i></p></html>'
					   ,'Nested repeat did not create expected outcome.'
					   )
				
	def testRepeatVarIndex (self):
		expectedResult = "<html>"
		for num in xrange (0,99):
			expectedResult += str (num)
		expectedResult += "</html>"
		
		self._runTest_ ('<html><p tal:repeat="var bigList" tal:omit-tag=""><b tal:replace="repeat/var/index">Index</b></p></html>'
					   ,expectedResult
					   ,"Repeat variable index failed."
					   )
					   
	def testRepeatVarNumber (self):
		self._runTest_ ('<html><p tal:repeat="var bigList" tal:omit-tag=""><b tal:replace="repeat/var/number">Index</b></p></html>'
					   ,'<html>123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899</html>'
					   ,'Repeat variable number failed.'
					   )
	def testRepeatVarEvenOdd (self):
		self._runTest_ ('<html><p tal:repeat="var fourList"><i tal:replace="var"></i> - <b tal:condition="repeat/var/odd">Odd</b><b tal:condition="repeat/var/even">Even</b></p></html>'
					   ,'<html><p>zero - <b>Even</b></p><p>one - <b>Odd</b></p><p>two - <b>Even</b></p><p>three - <b>Odd</b></p></html>'
					   ,'Repeat variables odd and even failed.'
					   )

	def testRepeatVarStartEnd (self):
		self._runTest_ ('<html><p tal:repeat="var fourList"><b tal:condition="repeat/var/start">Start</b><i tal:replace="var"></i><b tal:condition="repeat/var/end">End</b></p></html>'
					   ,'<html><p><b>Start</b>zero</p><p>one</p><p>two</p><p>three<b>End</b></p></html>'
					   ,'Repeat variables start and end failed.'
					   )
					   
	def testRepeatVarLength (self):
		self._runTest_ ('<html><p tal:repeat="var fourList"><b tal:condition="repeat/var/start">Len: <i tal:replace="repeat/var/length">length</i></b>Entry: <i tal:replace="var"></i></p></html>'
					   ,'<html><p><b>Len: 4</b>Entry: zero</p><p>Entry: one</p><p>Entry: two</p><p>Entry: three</p></html>'
					   ,'Repeat variable length failed.'
					   )
					   
	def testRepeatVarLowerLetter (self):
		self._runTest_ ('<html><p tal:repeat="var fourList"><i tal:replace="repeat/var/letter">a,b,c,etc</i>: <i tal:replace="var"></i></p></html>'
					   ,'<html><p>a: zero</p><p>b: one</p><p>c: two</p><p>d: three</p></html>'
					   ,'Repeat variable letter failed.'
					   )
		
	def testRepeatVarLowerLetterLarge (self):
		self._runTest_ ('<html><p tal:repeat="var bigList"><i tal:replace="repeat/var/letter">a,b,c,etc</i>: <i tal:replace="var"></i></p></html>'
					   ,'<html><p>a: 1</p><p>b: 2</p><p>c: 3</p><p>d: 4</p><p>e: 5</p><p>f: 6</p><p>g: 7</p><p>h: 8</p><p>i: 9</p><p>j: 10</p><p>k: 11</p><p>l: 12</p><p>m: 13</p><p>n: 14</p><p>o: 15</p><p>p: 16</p><p>q: 17</p><p>r: 18</p><p>s: 19</p><p>t: 20</p><p>u: 21</p><p>v: 22</p><p>w: 23</p><p>x: 24</p><p>y: 25</p><p>z: 26</p><p>ba: 27</p><p>bb: 28</p><p>bc: 29</p><p>bd: 30</p><p>be: 31</p><p>bf: 32</p><p>bg: 33</p><p>bh: 34</p><p>bi: 35</p><p>bj: 36</p><p>bk: 37</p><p>bl: 38</p><p>bm: 39</p><p>bn: 40</p><p>bo: 41</p><p>bp: 42</p><p>bq: 43</p><p>br: 44</p><p>bs: 45</p><p>bt: 46</p><p>bu: 47</p><p>bv: 48</p><p>bw: 49</p><p>bx: 50</p><p>by: 51</p><p>bz: 52</p><p>ca: 53</p><p>cb: 54</p><p>cc: 55</p><p>cd: 56</p><p>ce: 57</p><p>cf: 58</p><p>cg: 59</p><p>ch: 60</p><p>ci: 61</p><p>cj: 62</p><p>ck: 63</p><p>cl: 64</p><p>cm: 65</p><p>cn: 66</p><p>co: 67</p><p>cp: 68</p><p>cq: 69</p><p>cr: 70</p><p>cs: 71</p><p>ct: 72</p><p>cu: 73</p><p>cv: 74</p><p>cw: 75</p><p>cx: 76</p><p>cy: 77</p><p>cz: 78</p><p>da: 79</p><p>db: 80</p><p>dc: 81</p><p>dd: 82</p><p>de: 83</p><p>df: 84</p><p>dg: 85</p><p>dh: 86</p><p>di: 87</p><p>dj: 88</p><p>dk: 89</p><p>dl: 90</p><p>dm: 91</p><p>dn: 92</p><p>do: 93</p><p>dp: 94</p><p>dq: 95</p><p>dr: 96</p><p>ds: 97</p><p>dt: 98</p><p>du: 99</p></html>'
					   ,'Repeat variable letter failed on a large list.'
					   )
					   
	def testRepeatVarUpperLetter (self):
		self._runTest_ ('<html><p tal:repeat="var fourList"><i tal:replace="repeat/var/Letter">A,B,C,etc</i>: <i tal:replace="var"></i></p></html>'
					   ,'<html><p>A: zero</p><p>B: one</p><p>C: two</p><p>D: three</p></html>'
					   ,'Repeat variable Letter failed.'
					   )
					   
	def testRepeatVarLowerRoman (self):
		self._runTest_ ('<html><p tal:repeat="var bigList"><i tal:replace="repeat/var/roman">i,ii,iii,etc</i>: <i tal:replace="var"></i></p></html>'
					   ,'<html><p>i: 1</p><p>ii: 2</p><p>iii: 3</p><p>iv: 4</p><p>v: 5</p><p>vi: 6</p><p>vii: 7</p><p>viii: 8</p><p>ix: 9</p><p>x: 10</p><p>xi: 11</p><p>xii: 12</p><p>xiii: 13</p><p>xiv: 14</p><p>xv: 15</p><p>xvi: 16</p><p>xvii: 17</p><p>xviii: 18</p><p>xix: 19</p><p>xx: 20</p><p>xxi: 21</p><p>xxii: 22</p><p>xxiii: 23</p><p>xxiv: 24</p><p>xxv: 25</p><p>xxvi: 26</p><p>xxvii: 27</p><p>xxviii: 28</p><p>xxix: 29</p><p>xxx: 30</p><p>xxxi: 31</p><p>xxxii: 32</p><p>xxxiii: 33</p><p>xxxiv: 34</p><p>xxxv: 35</p><p>xxxvi: 36</p><p>xxxvii: 37</p><p>xxxviii: 38</p><p>xxxix: 39</p><p>xl: 40</p><p>xli: 41</p><p>xlii: 42</p><p>xliii: 43</p><p>xliv: 44</p><p>xlv: 45</p><p>xlvi: 46</p><p>xlvii: 47</p><p>xlviii: 48</p><p>xlix: 49</p><p>l: 50</p><p>li: 51</p><p>lii: 52</p><p>liii: 53</p><p>liv: 54</p><p>lv: 55</p><p>lvi: 56</p><p>lvii: 57</p><p>lviii: 58</p><p>lix: 59</p><p>lx: 60</p><p>lxi: 61</p><p>lxii: 62</p><p>lxiii: 63</p><p>lxiv: 64</p><p>lxv: 65</p><p>lxvi: 66</p><p>lxvii: 67</p><p>lxviii: 68</p><p>lxix: 69</p><p>lxx: 70</p><p>lxxi: 71</p><p>lxxii: 72</p><p>lxxiii: 73</p><p>lxxiv: 74</p><p>lxxv: 75</p><p>lxxvi: 76</p><p>lxxvii: 77</p><p>lxxviii: 78</p><p>lxxix: 79</p><p>lxxx: 80</p><p>lxxxi: 81</p><p>lxxxii: 82</p><p>lxxxiii: 83</p><p>lxxxiv: 84</p><p>lxxxv: 85</p><p>lxxxvi: 86</p><p>lxxxvii: 87</p><p>lxxxviii: 88</p><p>lxxxix: 89</p><p>xc: 90</p><p>xci: 91</p><p>xcii: 92</p><p>xciii: 93</p><p>xciv: 94</p><p>xcv: 95</p><p>xcvi: 96</p><p>xcvii: 97</p><p>xcviii: 98</p><p>xcix: 99</p></html>'
					   ,'Repeat variable roman failed.'
					   )
					   
	def testRepeatVarUpperRoman (self):
		self._runTest_ ('<html><p tal:repeat="var bigList"><i tal:replace="repeat/var/Roman">I,II,III,etc</i>: <i tal:replace="var"></i></p></html>'
					   ,'<html><p>I: 1</p><p>II: 2</p><p>III: 3</p><p>IV: 4</p><p>V: 5</p><p>VI: 6</p><p>VII: 7</p><p>VIII: 8</p><p>IX: 9</p><p>X: 10</p><p>XI: 11</p><p>XII: 12</p><p>XIII: 13</p><p>XIV: 14</p><p>XV: 15</p><p>XVI: 16</p><p>XVII: 17</p><p>XVIII: 18</p><p>XIX: 19</p><p>XX: 20</p><p>XXI: 21</p><p>XXII: 22</p><p>XXIII: 23</p><p>XXIV: 24</p><p>XXV: 25</p><p>XXVI: 26</p><p>XXVII: 27</p><p>XXVIII: 28</p><p>XXIX: 29</p><p>XXX: 30</p><p>XXXI: 31</p><p>XXXII: 32</p><p>XXXIII: 33</p><p>XXXIV: 34</p><p>XXXV: 35</p><p>XXXVI: 36</p><p>XXXVII: 37</p><p>XXXVIII: 38</p><p>XXXIX: 39</p><p>XL: 40</p><p>XLI: 41</p><p>XLII: 42</p><p>XLIII: 43</p><p>XLIV: 44</p><p>XLV: 45</p><p>XLVI: 46</p><p>XLVII: 47</p><p>XLVIII: 48</p><p>XLIX: 49</p><p>L: 50</p><p>LI: 51</p><p>LII: 52</p><p>LIII: 53</p><p>LIV: 54</p><p>LV: 55</p><p>LVI: 56</p><p>LVII: 57</p><p>LVIII: 58</p><p>LIX: 59</p><p>LX: 60</p><p>LXI: 61</p><p>LXII: 62</p><p>LXIII: 63</p><p>LXIV: 64</p><p>LXV: 65</p><p>LXVI: 66</p><p>LXVII: 67</p><p>LXVIII: 68</p><p>LXIX: 69</p><p>LXX: 70</p><p>LXXI: 71</p><p>LXXII: 72</p><p>LXXIII: 73</p><p>LXXIV: 74</p><p>LXXV: 75</p><p>LXXVI: 76</p><p>LXXVII: 77</p><p>LXXVIII: 78</p><p>LXXIX: 79</p><p>LXXX: 80</p><p>LXXXI: 81</p><p>LXXXII: 82</p><p>LXXXIII: 83</p><p>LXXXIV: 84</p><p>LXXXV: 85</p><p>LXXXVI: 86</p><p>LXXXVII: 87</p><p>LXXXVIII: 88</p><p>LXXXIX: 89</p><p>XC: 90</p><p>XCI: 91</p><p>XCII: 92</p><p>XCIII: 93</p><p>XCIV: 94</p><p>XCV: 95</p><p>XCVI: 96</p><p>XCVII: 97</p><p>XCVIII: 98</p><p>XCIX: 99</p></html>'
					   ,'Repeat variable Roman failed.'
					   )
					   
	def testLocalVarScope (self):
		self._runTest_ ('<html><p tal:repeat="var fourList"><b tal:replace="var">bold</b></p><b tal:condition="exists:var">VAR EXISTS</b></html>'
									 ,'<html><p>zero</p><p>one</p><p>two</p><p>three</p></html>'
									 ,'Local repeat variable remained accessible out of scope!'
									 )
		
if __name__ == '__main__':
	unittest.main()

