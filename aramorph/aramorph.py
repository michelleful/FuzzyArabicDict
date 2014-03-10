"""
Some code in here is taken from Alex Lee's pyaramorph port of the
Buckwalter Arabic Morphological Analyzer (GPL'ed)

Rewritten to use Redis (run "make_redis.py" first)
"""
import redis
r_server = redis.Redis("localhost")

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
            if (r_server.sismember("prefixes", prefix) and 
                r_server.sismember("stems", stem) and
                r_server.sismember("suffixes", suffix)):
                
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
    for prefix_entry in r_server.smembers("prefix:%s" % prefix):
        prefix_info = r_server.hgetall(prefix_entry)
        if debug: print prefix_entry, prefix_info
        
        # loop through possible stem entries
        for stem_entry in r_server.smembers("stem:%s" % stem):
            stem_info = r_server.hgetall(stem_entry)
            if debug: print stem_entry, stem_info
            
            # check the prefix-stem pair
            if not r_server.sismember("tableab", "%s %s" % (prefix_info["cat"], 
                                                            stem_info["cat"])):
                if debug: "\tPrefix %s and stem %s not in tableab" % (prefix_info["cat"], 
                                                                      stem_info["cat"])
                continue # skip if not compatible
            if debug: "\tPrefix %s and stem %s compatible" % (prefix_info["cat"], 
                                                              stem_info["cat"])

            # loop through possible suffix entries
            for suffix_entry in r_server.smembers("suffix:%s" % suffix):
                suffix_info = r_server.hgetall(suffix_entry)
                
                # check the prefix-suffix pair
                if not r_server.sismember("tableac", "%s %s" % (prefix_info["cat"],
                                                                suffix_info["cat"])):
                    continue

                # check the stem-suffix pair
                if not r_server.sismember("tablebc", "%s %s" % (stem_info["cat"],
                                                                suffix_info["cat"])):
                    continue

                # if we reached this point, the prefix-stem-suffix are compatible
                # return all the information necessary to display
                # what do we want?
                # 1. Arabic form (the original word)
                # 2. transliterated fully-vowelled form (TODO: split into pieces?)
                # 3. root of the stem (TODO)
                # 4. part of speech (just of the stem, or all?)
                # 5. gloss

                vowelled_form = prefix_info["vowelled"] + \
                                stem_info["vowelled"] + \
                                suffix_info["vowelled"]

                pos = stem_info["pos"]

                gloss = "%s + %s + %s" % (prefix_info["gloss"], stem_info["gloss"], suffix_info["gloss"])
                gloss = gloss.strip().strip("+").strip()

                solutions.append({'word': translate_b2u(word), 'vowelled': vowelled_form, 'pos': pos, 'gloss': gloss})
                
    return solutions

