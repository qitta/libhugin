#!/usr/bin/env python
# encoding: utf-8

# stdlib
from itertools import combinations

# hugin
import hugin.analyze as plugin


class GenreCmp(plugin.IComparator):

    def compare(self, movie_a, movie_b):
        pass

    def compare_all(self, database, threshold=0.51, attr_name='genre'):
        for a, b in combinations(database.values(), 2):
            if a.attributes.get(attr_name) and b.attributes.get(attr_name):
                distance = self._genre_distance(a, b, attr_name)
                if distance > threshold:
                    a.comparator_data.setdefault(self.name, set()).add(
                        (b, distance)
                    )
                    b.comparator_data.setdefault(self.name, set()).add(
                        (a, distance)
                    )

##############################################################################
# -------------------------- helper functions --------------------------------
##############################################################################

    def _genre_distance(self, a, b, attr):
        """ Calculate the 'distance' between two genres

        """
        a, b = set(a.attributes.get(attr)), set(b.attributes.get(attr))
        return len(a & b) / max(len(a), len(b))
