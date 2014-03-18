# data structures for all the Aramorph info

class Morpheme(object):    
    def __init__(self, vowelled, cat, pos, gloss):
        self.vowelled   = vowelled
        self.gloss      = gloss
        self.cat        = cat # for verifying compatibility
        self.pos        = pos # human-readable part of speech
        
# this is what we'll pickle
class AramorphInfo(object):
    def __init__(self, prefixes, stems, suffixes, ab, bc, ac):
        self.prefixes = prefixes # key=unvowelled, 
        self.stems = stems       # value = list of Morphemes
        self.suffixes = suffixes
        self.ab = ab # key = LHS cat. value = list of compatible RHS cats.
        self.bc = bc
        self.ac = ac
        
    def is_valid_prefix(self, unvowelled_prefix):
        return unvowelled_prefix in ai.prefixes
        
    def is_valid_stem(self, unvowelled_stem):
        return unvowelled_stem in ai.stems

    def is_valid_suffix(self, unvowelled_suffix):
        return unvowelled_suffix in ai.suffixes
        
    def are_prefix_stem_compatible(self, prefix_morpheme, stem_morpheme):
        return stem_morpheme.cat in ai.ab[prefix_morpheme.cat]
        
    def are_stem_suffix_compatible(self, stem_morpheme, suffix_morpheme):
        return suffix_morpheme.cat in ai.bc[stem_morpheme.cat]

    def are_prefix_suffix_compatible(self, prefix_morpheme, suffix_morpheme):
        return suffix_morpheme.cat in ai.ac[prefix_morpheme.cat]

