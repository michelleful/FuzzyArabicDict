# helper functions for converting from Buckwalter to Unicode and vice versa

buck = u"'|>&<}AbptvjHxd*rzs$SDTZEg_fqklmnhwYyFNKaui~o0123456789`{"
unic = u"".join(map(unichr,
             list(range(0x0621, 0x063b)) + # hamza through ghayn
             list(range(0x0640, 0x0653)) + # taTwiil through sukuun
             list(range(0x0660, 0x066A)) + # numerals
             list(range(0x0670, 0x0672)))) # dagger 'alif, waSla

buck2unic = dict(zip([ord(letter) for letter in buck], unic))
unic2buck = dict(zip([ord(letter) for letter in unic], buck))

def translate_b2u(buckwalter_string):
    return buckwalter_string.translate(buck2unic)

def translate_u2b(unicode_string):
    return unicode_string.translate(unic2buck)

