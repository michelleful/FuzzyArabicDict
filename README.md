FuzzyArabicDict
===============

Dictionary app that allows you to look up Arabic words in transliteration

This is basically Python glue to bring together work by others, particularly:
- [Yamli](http://yamli.com) Arabic transliteration 
- Buckwalter Arabic Morphological Analyzer [LDC2002L49](http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC2002L49)

TODO:
- [x] Figure out how to access words returned by Yamli
- [ ] Work out how to use Aramorpher.cpp
- [ ] Write Python binding for Aramorpher.cpp
- [ ] Make Python back-end to take an Arabic word and return results from PyAramorph via AJAX (use Ember.js?)
- [ ] Format webpage to display results nicely
