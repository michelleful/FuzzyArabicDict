# -*- coding: utf-8 -*-

import re

# helper functions for converting from Buckwalter to Unicode and vice versa

buck = u"'|>&<}AbptvjHxd*rzs$SDTZEg_fqklmnhwYyFNKaui~o0123456789`{"
unic = u"".join(map(unichr,
             list(range(0x0621, 0x063b)) + # hamza through ghayn
             list(range(0x0640, 0x0653)) + # taTwiil through sukuun
             list(range(0x0660, 0x066A)) + # numerals
             list(range(0x0670, 0x0672)))) # dagger 'alif, waSla

# more reader-friendly transliteration - ALA/Wehr 
ala  = [# hamza through ghayn
        u"ʾ",u"ʾā",u"ʾ",u"ʾ",u"ʾ",u"ʾ",u"ā",u"b",u"h",u"t",u"ṯ",u"j",u"ḥ",u"ḵ",
        u"d",u"ḏ",u"r",u"z",u"s",u"š",u"ṣ",u"ḍ",u"ṭ",u"ẓ",u"ʿ",u"ḡ",
        # taTwiil through sukuun
        u"",u"f",u"q",u"k",u"l",u"m",u"n",u"h",u"w",u"ā",u"y",
        u"an",u"un",u"in",u"a",u"u",u"i",u"~",u"",
        # numerals
        u"0",u"1",u"2",u"3",u"4",u"5",u"6",u"7",u"8",u"9",
        # dagger 'alif, waSla
        u"ā",u""]

assert len(buck) == len(unic) == len(ala)

buck2unic = dict(zip([ord(letter) for letter in buck], unic))
unic2buck = dict(zip([ord(letter) for letter in unic], buck))

def b2u(buckwalter_string):
    string = unicode(buckwalter_string).translate(buck2unic)
    return string.replace(u"\u0671", u"\u0627") 
    # because alef wasla doesn't show up properly in most fonts

def u2b(unicode_string):
    return unicode_string.translate(unic2buck)

def b2ala_letter(letter):
    try:
        return ala[buck.index(letter)]
    except:
        return letter

def b2ala(buckwalter_string):
    # deal with shadda (doubled letters)
    string = re.sub(r"(.)~", r"\1\1", buckwalter_string)

    string = u"".join([b2ala_letter(letter) for letter in string])

    # deal with uw, iy - make them ū and ī
    # might not be 100% correct - should they remain "uw", "iy" in some contexts?
    string = string.replace(u"uw", u"ū")
    string = string.replace(u"iy", u"ī")
    
    # deal with repeated vowels    
    string = string.replace(u"aan", "an") # nunated alif
    string = string.replace(u"āa", u"ā")
    string = string.replace(u"ūu", u"ū")

    # special case - 3 l's in Allah because there are 2 written l's 
    # and one has a shadda
    string = string.replace(u"lll", u"ll")

    return string
