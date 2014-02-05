#!/usr/bin/env python
# encoding: utf-8

from itertools import combinations
# hugin
import hugin.analyze as plugin


class GenreCmp(plugin.IComparator):

    def compare(self, movie_a, movie_b):
        pass

    def process_db(self, database, threshold=0.51):
        for a, b in combinations(database.values(), 2):
            if a.attributes.get('genre') and b.attributes.get('genre'):
                distance = self._genre_distance(a, b)
                if distance > threshold:
                    a.comparator_data.setdefault(self.name, set()).add(
                        (b, distance)
                    )
                    b.comparator_data.setdefault(self.name, set()).add(
                        (a, distance)
                    )

    def _genre_distance(self, a, b):
        """ Calculate the 'distance' between two genres

        """
        a, b = set(a.attributes.get('genre')), set(b.attributes.get('genre'))
        return len(a & b) / max(len(a), len(b))
