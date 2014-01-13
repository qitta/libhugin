#!/usr/bin/env python
# encoding: utf-8

from guess_language import guess_language
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance

# hugin
import hugin.analyze as plugin

class KeywordCmp(plugin.IAnalyzer):

    def process_movie(self, movie):
        pass


    def process_database(self, database):
        for a, b in combinations(database.values(), 2):
            if a.attributes.get('keywords') and b.attributes.get('keywords'):
                pass



