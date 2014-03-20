FuzzyArabicDict
===============

Dictionary app that allows you to look up Arabic words in transliteration

This is basically Python glue to bring together work by others, particularly:
- [Yamli](http://yamli.com) Arabic transliteration 
- Buckwalter Arabic Morphological Analyzer [LDC2002L49](http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC2002L49)

You can now use this online at [http://fuzzyarabic.herokuapp.com/](http://fuzzyarabic.herokuapp.com/)

How to run this locally:
- Have Flask installed (or `pip install -r requirements.txt`)
- python fuzzy.py
- Point your browser to localhost:5000
- Note that you must still be connected to the Internet for the Yamli web service and thereby the whole app to work
