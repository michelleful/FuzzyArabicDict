"""
This loads the pickled Aramorpher object, making it available to do analysis

Run this first:
> python make_pickle.py
"""
import cPickle as pickle
import os
import sys

# this is a hacky (?) way of getting the pickled object in a subdirectory
# to load properly when called from an upper-level directory
import aramorpher
sys.modules["aramorpher"] = aramorpher

dir = os.path.dirname(__file__)
if dir:
    # os.path.join
    dir += "/"

with open(dir + "aramorph.data", "rb") as f:
    ai = pickle.load(f) 

