#!/usr/bin/env python
# encoding: utf-8

from itertools import combinations
import math

from guess_language import guess_language
from collections import Counter

# hugin
import hugin.analyze as plugin

class KeywordCmp(plugin.IAnalyzer):

    def process_movie(self, movie):
        pass

    def process_database(self, database):
        for a, b in combinations(database.values(), 2):
            keywords_a = a.analyzer_data.get('KeywordExtractor')
            keywords_b = b.analyzer_data.get('KeywordExtractor')
            if keywords_a and keywords_b:
                rating = self._compare_keywords(keywords_a, keywords_b)
                rating = sum(rating.values())/len(rating)
                a.analyzer_data.setdefault(self.name, set()).add(
                    (b, rating)
                )
                b.analyzer_data.setdefault(self.name, set()).add(
                    (a, rating)
               )

    def _compare_keywords(self, keywords_a, keywords_b):
        result = {}
        grouped_a = self._group_by_length(keywords_a)
        grouped_b = self._group_by_length(keywords_b)
        for cnt_a, group_a in grouped_a.items():
            result[cnt_a] = 0
            for cnt_b, group_b in grouped_b.items():
                if cnt_a == cnt_b:
                    rating = self._compare(group_a, group_b, cnt_a)
                    result[cnt_a] += rating/min(len(group_a), len(group_b))

        return result

    def _group_by_length(self, keywords):
        cnt = Counter()
        for keyword in keywords:
            cnt.setdefault(len(keyword), []).append(keyword)
        return cnt

    def _compare(self, a, b, cnt):
        return len(frozenset(tuple(a[0])) & frozenset(tuple(b[0]))) / cnt
