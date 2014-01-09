#!/usr/bin/env python
# encoding: utf-8

from itertools import combinations
# hugin
import hugin.analyze as plugin

class GenreCmp(plugin.IAnalyzer):

    def process_movie(self, movie_a, movie_b):
        pass

    def process_database(self, database):
        genre_distances = []
        for a, b in combinations(database.values(), 2):
            genre_distances.append((b, self._genre_distance(a, b)))


    def _genre_distance(self, a, b):
        if a.attributes.get('genre') and b.attributes.get('genre'):
            return  len(set(a.attributes.get('genre')) | set(b.attributes.get('genre'))) / len(set(a.attributes.get('genre')))
