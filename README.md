FuzzyArabicDict
===============

Dictionary app that allows you to look up Arabic words in transliteration

This is basically Python glue to bring together work by others, particularly:
- [Yamli](http://yamli.com) Arabic transliteration 
- Buckwalter Arabic Morphological Analyzer [LDC2002L49](http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC2002L49)

HOWTO run this locally:
- Run aramorph/make_redis.py (make sure you have Redis and the Python Redis module installed)
- python fuzzy.py
- Navigate to localhost:5000
- Note that you must be connected to the Internet for the Yamli web service and thereby the whole app to work
