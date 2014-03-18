"""
Some code in here is taken from Alex Lee's pyaramorph port of the
Buckwalter Arabic Morphological Analyzer (GPL'ed)

Run this first:
> python make_pickle.py
"""
from make_pickle import *

import os
dir = os.path.dirname(__file__)
if dir: dir += "/"
f = open(dir + "aramorph.info", "rb")
ai = pickle.load(f)

from transliterate import * # transliteration methods

def segment(word):
    """ Create possible segmentations of the given word """
    segments = []
    prelen = 0
    suflen = 0
    strlen = len(word)

    while prelen <= 4:
        # This loop increases the prefix length until > 4
        prefix = word[0:prelen]
        stemlen = strlen - prelen
        suflen = 0

        while stemlen >= 1 and suflen <= 6:
            # This loop increases suffix length until > 6,
            # or until stem length < 1
            stem = word[prelen:(prelen+stemlen)]
            suffix = word[(prelen+stemlen):]
            segments.append((prefix, stem, suffix))
            
            stemlen -= 1
            suflen += 1

        prelen += 1

    return segments

def analyse_arabic(word, debug=False):
    """Find possible solutions for the given UTF8 Arabic word"""
    buck_word = translate_u2b(word)
    if debug: print "Analysing ", word, "\t", buck_word
    return analyse(buck_word, debug)

def analyse(word, debug=False):
    """Find possible solutions for the given word"""
    results = []
    count = 0

    for alternative in alternatives(word):
        for (prefix, stem, suffix) in segment(alternative):
            if (ai.is_valid_prefix(prefix) and 
                ai.is_valid_stem(stem) and
                ai.is_valid_suffix(suffix)):
                
                solutions = check_compatibility(alternative, 
                                                prefix, stem, suffix, debug)
                for solution in solutions:
                    if solution not in results:
                        results.append(solution)
    return results

def alternatives(word):
    """Add some spelling alternatives"""
    alts = [word]
    if word.endswith('w'): alts.append(word + 'A')
    # e.g. yktbw -> yktbwA, which is what Buckwalter is looking for
    return alts

def check_compatibility(word, prefix, stem, suffix, debug=False):
    """Returns all possible compatible solutions of a prefix, stem and suffix"""
    solutions = []

    if debug: print "Checking compatibility of %s = %s + %s + %s" % (word, 
                                                        prefix, stem, suffix)
    
    # loop through possible prefix entries
    for prefix_entry in ai.prefixes[prefix]:        
        # loop through possible stem entries
        for stem_entry in ai.stems[stem]:
            # check if prefix and stem are compatible
            if not ai.are_prefix_stem_compatible(prefix_entry, stem_entry):
                continue
            # valid prefix and stem combo, so continue
            # loop through possible suffix entries
            for suffix_entry in ai.suffixes[suffix]:
                if not ai.are_stem_suffix_compatible(stem_entry, suffix_entry):
                    continue
                if not ai.are_stem_suffix_compatible(stem_entry, suffix_entry):
                    continue

                # if we reached this point, the prefix-stem-suffix are compatible
                # return all the information necessary to display
                # what do we want?
                # 1. Arabic form (the original word)
                # 2. transliterated fully-vowelled form (TODO: split into pieces?)
                # 3. root of the stem (TODO)
                # 4. part of speech (just of the stem, or all?)
                # 5. gloss

                vowelled_form = prefix_entry.vowelled + \
                                stem_entry.vowelled + \
                                suffix_entry.vowelled

                pos = stem_entry.pos

                gloss = "%s + %s + %s" % (prefix_entry.gloss, stem_entry.gloss, suffix_entry.gloss)
                gloss = gloss.strip().strip("+").strip()

                solutions.append({'word': translate_b2u(word), 
                                  'vowelled': translate_b2u(vowelled_form),
                                  'transliteration': translate_b2ala(vowelled_form), 
                                  'pos': pos, 
                                  'gloss': gloss})
                
    return solutions

