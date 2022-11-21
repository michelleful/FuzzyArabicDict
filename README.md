FuzzyArabicDict
===============

Dictionary app that allows you to look up Arabic words in transliteration

This is basically Python glue to bring together work by others, particularly:
- [Yamli](http://yamli.com) Arabic transliteration 
- Buckwalter Arabic Morphological Analyzer [LDC2002L49](http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC2002L49)

> **Note**
> Please note that the URL has changed, due to Heroku removing its free tier. The CSS is a little off; I
haven't had time to fix it.

You can now use this online at [https://fuzzy-arabic-dict.onrender.com/](https://fuzzy-arabic-dict.onrender.com/)

How to run this locally:
- Have Flask installed (or `pip install -r requirements.txt`)
- `flask --app fuzzy run`
- Point your browser to localhost:5000
- Note that you must still be connected to the Internet for the Yamli web service and thereby the whole app to work
