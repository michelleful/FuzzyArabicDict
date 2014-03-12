import re
import redis
from collections import defaultdict

r_server = redis.Redis("localhost")

# first remove all keys
r_server.flushdb()

def process_textfile(filename):
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(';'):
                continue
            try:
                (unvowelled, vowelled, cat, gloss) = line.split('\t')
                # strip after we've done the split so that the 
                # zero prefix/suffix is handled correctly
                yield (unvowelled, vowelled, cat, gloss.strip())
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
        elif cat.startswith('N') and p_AZ.search(gloss):
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

def add_morpheme_to_redis(morpheme_type, morpheme_dict, 
                          unvowelled, vowelled, cat, gloss, root=None):
    if morpheme_type.endswith('x'):
        plural = morpheme_type + 'es'
    else:
        plural = morpheme_type + 's'

    # add morpheme to set of morphemes "prefixes", "stems" or "suffixes"
    r_server.sadd(plural, unvowelled)

    # make pos and gloss more human-readable
    pos, gloss = process_pos(vowelled, cat, gloss)

    # there could be multiple morphemes with the same unvowelled form
    # so create a set of morpheme types with this unvowelled form
    # and add a number to disambiguate them
    morpheme_dict[unvowelled] += 1
    r_server.sadd("%s:%s" % (morpheme_type, unvowelled), 
                  "%s:%s:%s" % (morpheme_type, unvowelled, morpheme_dict[unvowelled]))
    r_server.hmset("%s:%s:%s" % (morpheme_type, unvowelled, morpheme_dict[unvowelled]), 
                    {"unvowelled": unvowelled, 
                     "vowelled": vowelled, 
                     "cat": cat, 
                     "pos": pos,
                     "gloss": gloss})
    if root:
        r_server.hset("%s:%s:%s" % (morpheme_))
    
prefix_dict = defaultdict(int)
def process_prefixes():
    for (unvowelled, vowelled, cat, gloss) in process_textfile("dictprefixes"):    
        add_morpheme_to_redis("prefix", prefix_dict, unvowelled, vowelled, cat, gloss)

suffix_dict = defaultdict(int)
def process_suffixes():
    for (unvowelled, vowelled, cat, gloss) in process_textfile("dictsuffixes"):    
        add_morpheme_to_redis("suffix", suffix_dict, unvowelled, vowelled, cat, gloss)

stem_dict = defaultdict(int)
def process_stems():
    for (unvowelled, vowelled, cat, gloss) in process_textfile("dictstems"):    
        add_morpheme_to_redis("stem", stem_dict, unvowelled, vowelled, cat, gloss)

def process_tableXY(filename):
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(';'):
                continue
            r_server.sadd(filename, line.strip())

process_prefixes()
process_stems()
process_suffixes()
process_tableXY("tableab")
process_tableXY("tablebc")
process_tableXY("tableac")


