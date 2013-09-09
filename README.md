FuzzyArabicDict
===============

Dictionary app that allows you to look up Arabic words in transliteration

This is basically Python glue to bring together work by others, particularly:
- [Yamli](http://yamli.com) Arabic transliteration 
- Buckwalter Arabic Morphological Analyzer [LDC2002L49](http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC2002L49)

TODO:
- [x] Figure out how to access words returned by Yamli
- [ ] Rewrite PyAramorph to (i) use a Redis backend and (ii) return results in a nice json package
- [ ] Make Flask back-end to take a list of Arabic words and return results from PyAramorph via AJAX (use Ember.js?)
- [ ] Format webpage to display results nicely
