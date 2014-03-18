# Explore using a pickled file rather than redis

import cPickle as pickle
from collections import defaultdict
from dataclass import Morpheme, AramorphInfo
from process_files import process_textfile, process_tableXY

prefixes = defaultdict(list)
stems    = defaultdict(list)
suffixes = defaultdict(list)

ab = defaultdict(list)
bc = defaultdict(list)
ac = defaultdict(list)

def process_prefixes():
    for (unvowelled, vowelled, cat, pos, gloss) in process_textfile("dictprefixes"):
        prefixes[unvowelled].append(Morpheme(vowelled, cat, pos, gloss))

def process_stems():
    for (unvowelled, vowelled, cat, pos, gloss) in process_textfile("dictstems"):
        stems[unvowelled].append(Morpheme(vowelled, cat, pos, gloss))

def process_suffixes():
    for (unvowelled, vowelled, cat, pos, gloss) in process_textfile("dictsuffixes"):
        suffixes[unvowelled].append(Morpheme(vowelled, cat, pos, gloss))

def process_tableAB():
    for (left, right) in process_tableXY("tableab"):
        ab[left].append(right)

def process_tableBC():
    for (left, right) in process_tableXY("tablebc"):
        bc[left].append(right)

def process_tableAC():
    for (left, right) in process_tableXY("tableac"):
        ac[left].append(right)

if __name__ == "__main__":
    process_prefixes()
    process_stems()
    process_suffixes()
    process_tableAB()
    process_tableBC()
    process_tableAC()

    # now construct AramorphInfo
    aramorph = AramorphInfo(prefixes, stems, suffixes, ab, bc, ac)

    # and pickle it
    pickle.dump(aramorph, open("aramorph.info", "wb"), pickle.HIGHEST_PROTOCOL)
