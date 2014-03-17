import redis
from collections import defaultdict
from process_files import process_textfile, process_tableXY

r_server = redis.Redis("localhost")

# first remove all keys
r_server.flushdb()

def add_morpheme_to_redis(morpheme_type, morpheme_dict, 
                          unvowelled, vowelled, cat, pos, gloss, root=None):
    if morpheme_type.endswith('x'):
        plural = morpheme_type + 'es'
    else:
        plural = morpheme_type + 's'

    # add morpheme to set of morphemes "prefixes", "stems" or "suffixes"
    r_server.sadd(plural, unvowelled)

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

def process_morpheme_file_for_redis(filename, morpheme_type, morpheme_dict):
    for (unvowelled, vowelled, cat, pos, gloss) in process_textfile(filename):
        add_morpheme_to_redis(morpheme_type, morpheme_dict, 
                              unvowelled, vowelled, cat, pos, gloss)

def process_tableXY_for_redis(filename):
    for (left, right) in process_tableXY(filename):
        r_server.sadd(filename, " ".join([left, right]))

# -------------
#    MAIN
# -------------
prefix_dict = defaultdict(int)
stem_dict = defaultdict(int)
suffix_dict = defaultdict(int)

process_morpheme_file_for_redis("dictprefixes", "prefix", prefix_dict)
process_morpheme_file_for_redis("dictstems", "stem", stem_dict)
process_morpheme_file_for_redis("dictsuffixes", "suffix", suffix_dict)

process_tableXY_for_redis("tableab")
process_tableXY_for_redis("tablebc")
process_tableXY_for_redis("tableac")


