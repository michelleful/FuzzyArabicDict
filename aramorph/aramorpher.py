"""
Data classes - Aramorpher includes all the analysis logic

Some code in here is taken from Alex Lee's pyaramorph port of the
Buckwalter Arabic Morphological Analyzer (GPL'ed)

Run this first:
> python make_pickle.py
"""
import transliterate

class Morpheme(object):
    def __init__(self, vowelled, cat, pos, gloss, root):
        self.vowelled   = vowelled
        self.gloss      = gloss
        self.cat        = cat  # for verifying compatibility
        self.pos        = pos  # human-readable part of speech
        self.root       = root # only really valid for (a subset of) stems, 
                               # empty for everything else
                               
        def __str__(self):
            return "%s (%s) %s %s %s" % (self.vowelled, self.root, self.cat, self.pos, self.gloss)
        
        def __repr__(self):
            return self.__str__()
        
# this is what we'll pickle
class Aramorpher(object):

    def __init__(self, prefixes, stems, suffixes, ab, bc, ac):
        self.prefixes = prefixes # key=unvowelled, 
        self.stems = stems       # value = list of Morphemes
        self.suffixes = suffixes
        self.ab = ab # key = LHS cat. value = list of compatible RHS cats.
        self.bc = bc
        self.ac = ac
        
    def is_valid_prefix(self, unvowelled_prefix):
        return unvowelled_prefix in self.prefixes
        
    def is_valid_stem(self, unvowelled_stem):
        return unvowelled_stem in self.stems

    def is_valid_suffix(self, unvowelled_suffix):
        return unvowelled_suffix in self.suffixes
        
    def are_prefix_stem_compatible(self, prefix_morpheme, stem_morpheme):
        return stem_morpheme.cat in self.ab[prefix_morpheme.cat]
        
    def are_stem_suffix_compatible(self, stem_morpheme, suffix_morpheme):
        return suffix_morpheme.cat in self.bc[stem_morpheme.cat]

    def are_prefix_suffix_compatible(self, prefix_morpheme, suffix_morpheme):
        return suffix_morpheme.cat in self.ac[prefix_morpheme.cat]

    def segment(self, word):
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

    def analyse_arabic(self, word):
        """Find possible solutions for the given UTF8 Arabic word"""
        buck_word = transliterate.u2b(word)
        return self.analyse(buck_word)

    def analyse(self, word):
        """Find possible solutions for the given word"""
        results = []
        count = 0

        for alternative in self.alternatives(word):
            for (prefix, stem, suffix) in self.segment(alternative):
                if (self.is_valid_prefix(prefix) and 
                    self.is_valid_stem(stem) and
                    self.is_valid_suffix(suffix)):
                    
                    solutions = self.check_compatibility(alternative, 
                                                    prefix, stem, suffix)
                    for solution in solutions:
                        if solution not in results:
                            results.append(solution)
        return results

    def alternatives(self, word):
        """Add some spelling alternatives"""
        alts = [word]
        if word.endswith('w'): alts.append(word + 'A')
        # e.g. yktbw -> yktbwA, which is what Buckwalter is looking for
        return alts

    def check_compatibility(self, word, prefix, stem, suffix):
        """Returns all possible compatible solutions of a prefix, stem and suffix"""
        solutions = []
        
        # loop through possible prefix entries
        for prefix_entry in self.prefixes[prefix]:        
            # loop through possible stem entries
            for stem_entry in self.stems[stem]:
                # check if prefix and stem are compatible
                if not self.are_prefix_stem_compatible(prefix_entry, stem_entry):
                    continue
                # valid prefix and stem combo, so continue
                # loop through possible suffix entries
                for suffix_entry in self.suffixes[suffix]:
                    if not self.are_stem_suffix_compatible(stem_entry, suffix_entry):
                        continue
                    if not self.are_stem_suffix_compatible(stem_entry, suffix_entry):
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

                    gloss = "%s + %s + %s" % (prefix_entry.gloss, stem_entry.gloss, suffix_entry.gloss)
                    gloss = gloss.strip().strip("+").strip()

                    solutions.append({'word': transliterate.b2u(word), 
                                      'vowelled': transliterate.b2u(vowelled_form),
                                      'transliteration': transliterate.b2ala(vowelled_form), 
                                      'root': transliterate.b2u(stem_entry.root),
                                      'pos': stem_entry.pos, 
                                      'gloss': gloss})
                
        return solutions

    def information(self, words):
        """Return unglossed information for a list of Arabic words (used when analyse() turned up empty)"""
        solutions = list()
        for word in words:
            solutions.append({'word': word,
                              'vowelled': "",
                              'transliteration': transliterate.b2ala(transliterate.u2b(word)),
                              'pos': "",
                              'root': "",
                              'gloss': "Not found in dictionary"})
        return solutions
