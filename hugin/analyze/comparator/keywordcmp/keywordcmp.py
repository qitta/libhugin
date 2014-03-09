#!/usr/bin/env python
# encoding: utf-8

# stdlib
from itertools import combinations
from collections import Counter

# hugin
import hugin.analyze as plugin


class KeywordCmp(plugin.IComparator):

    def compare(self, movie_a, movie_b):
        pass

    def process_db(self, database, attr_name='KeywordExtractor'):
        for a, b in combinations(database.values(), 2):
            keywords_a = a.comparator_data.get(attr_name)
            keywords_b = b.comparator_data.get(attr_name)
            if keywords_a and keywords_b:
                rating = self._compare_keywords(keywords_a, keywords_b)
                rating = sum(rating.values()) / len(rating)
                a.comparator_data.setdefault(self.name, set()).add(
                    (b, rating)
                )
                b.comparator_data.setdefault(self.name, set()).add(
                    (a, rating)
                )

##############################################################################
# -------------------------- helper functions --------------------------------
##############################################################################

    def _compare_keywords(self, keywords_a, keywords_b):
        result = {}
        grouped_a = self._group_by_length(keywords_a)
        grouped_b = self._group_by_length(keywords_b)
        for cnt_a, group_a in grouped_a.items():
            result[cnt_a] = 0
            for cnt_b, group_b in grouped_b.items():
                if cnt_a == cnt_b:
                    rating = self._compare(group_a, group_b, cnt_a)
                    result[cnt_a] += rating / min(len(group_a), len(group_b))

        return result

    def _group_by_length(self, keywords):
        cnt = Counter()
        for keyword in keywords:
            cnt.setdefault(len(keyword), []).append(keyword)
        return cnt

    def _compare(self, a, b, cnt):
        return len(frozenset(tuple(a[0])) & frozenset(tuple(b[0]))) / cnt
