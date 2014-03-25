import re

def process_textfile(filename):
    root = '' # should always be empty for prefixes and suffixes
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(';--- '): # this contains the root for the following lines
                # root is the first word (might be followed by comments), 
                # up to the first bracket (sometimes there's "ktb(1)" etc.)
                root = line.replace(';--- ','').split()[0].split('(')[0]
                
                if "/" in root:
                    # Buckwalter gives possible variants of root, e.g.
                    # Axw/y = Axw or Axy
                    # nw/yf = nwf or nyf
                    # it's always a w/y thing
                    # go with /w/ as Hans Wehr almost always shows a /w/ as a variant
                    root = root.replace("w/y","w")
                
            elif line.startswith(';-----'): # "reset" line for when there's no root
                root = ''
            elif line.startswith(';'):
                continue
            try:
                (unvowelled, vowelled, cat, gloss) = line.split('\t')
                # strip after we've done the split so that the 
                # zero prefix/suffix is handled correctly

                # make pos and gloss more human-readable
                pos, gloss = process_pos(vowelled, cat, gloss)
 
                # concept of a root is usually useless when word is a proper noun               
                if pos == "Proper noun":
                    local_root = ""
                else:
                    local_root = root
                    
                yield (unvowelled, vowelled, cat, pos, gloss, local_root)
            except:
                continue

p_AZ = re.compile('^[A-Z]')
p_iy = re.compile('iy~$')

pos_replacement = {
    'ADJ': 'Adjective',
    'ADV': 'Adverb',
    'ABBREV': 'Abbreviation',
    'PREP': 'Preposition',
    'NEG_PART': 'Negative particle',
    'CONJ': 'Conjunction',
    'INTERJ': 'Interjection',
    'NOUN_PROP': 'Proper noun',
    'FUNC_WORD': 'Function word',
    'REL_PRON': 'Relative pronoun',
    'DET': 'Determiner',
    'DEM_PRON': 'Demonstrative pronoun',
    'INTERROG_PART': 'Interrogative pronoun',
    'FUT_PART': 'Future particle'
}

def process_pos(voc, cat, glossPOS):
    m = re.search('<pos>.*/(.+?)</pos>', glossPOS)
    if m:
        POS = m.group(1)
        gloss = glossPOS
        # replace abbreviations as above with their long forms
        for pos_type, long_pos_type in pos_replacement.items():
            if pos_type.startswith(POS):
                POS = long_pos_type
    else:
        gloss = glossPOS
        if cat.startswith('Pref-0') or cat.startswith('Suff-0'):
            POS = "" # null prefix or suffix
        elif cat.startswith('F'):
            POS = "Function word"
        elif cat.startswith('IV'):
            POS = "Imperfect verb"
        elif cat.startswith('PV'):
            POS = "Perfect verb"
        elif cat.startswith('CV'):
            POS = "Imperative verb"
        elif cat.startswith('N') and p_AZ.search(gloss): # gloss starts with a capital letter
            POS = "Proper noun" # educated guess, (99% correct)
        elif cat.startswith('N') and p_iy.search(voc):
            POS = "Noun" # (was NOUN_ADJ: some of these are really ADJ' and need to be tagged manually)
        elif cat.startswith('N'):
            POS = "Noun"
        elif POS.startswith('ADJ'):
            POS = "Adjective"
        else:
            print "no POS can be deduced for %s" % voc
            assert False

    # make POS sentence case
    POS = POS.capitalize()

    gloss = re.sub('<pos>.+?</pos>', '', gloss)
    gloss = gloss.strip()
    return POS, gloss

def process_tableXY(filename):
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(';'):
                continue
            yield line.strip().split()

