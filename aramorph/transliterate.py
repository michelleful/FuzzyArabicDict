# -*- coding: utf-8 -*-

import re

# helper functions for converting from Buckwalter to Unicode and vice versa

buck = u"'|>&<}AbptvjHxd*rzs$SDTZEg_fqklmnhwYyFNKaui~o0123456789`{"
unic = u"".join(map(unichr,
             list(range(0x0621, 0x063b)) + # hamza through ghayn
             list(range(0x0640, 0x0653)) + # taTwiil through sukuun
             list(range(0x0660, 0x066A)) + # numerals
             list(range(0x0670, 0x0672)))) # dagger 'alif, waSla
ala  = ["ʾ","|","ʾ","ʾ","ʾ","ʾ","ā","b","ah","t","th","j","ḥ","kh",
        "d","dh","r","z","s","sh","ṣ","ḍ","ṭ","ẓ","ʿ","gh","","f","q","k","l",
        "m","n","h","w","ā","y","an","un","in","a","u","i","~","",
        "0","1","2","3","4","5","6","7","8","9","`","{"]

assert len(buck) == len(unic) == len(ala)

buck2unic = dict(zip([ord(letter) for letter in buck], unic))
unic2buck = dict(zip([ord(letter) for letter in unic], buck))

def translate_b2u(buckwalter_string):
    return unicode(buckwalter_string).translate(buck2unic)

def translate_u2b(unicode_string):
    return unicode_string.translate(unic2buck)

def translate_b2ala(buckwalter_string):
    # deal with shadda (doubled letters)
    string = re.sub(r"(.)~", r"\1\1", buckwalter_string)

    string = "".join([ala[buck.index(letter)] for letter in string])
    # deal with madda
    # TODO
    
    # deal with uw, iy
    
    return string
