#!/usr/bin/env python
# encoding: utf-8

# hugin
import hugin.analyze as plugin
from hugin.analyze.rake import extract_keywords


class KeywordExtractor(plugin.IAnalyzer):

    def analyze(self, movie, score_threshold=1.0, attr_name='plot'):
        if movie.attributes.get(attr_name):
            lang, keywords = extract_keywords(
                movie.attributes.get(attr_name), use_stemmer=False
            )
            keywordlist = []
            for keyword, score in keywords.items():
                if score > score_threshold:
                    keywordlist.append(list(keyword))
            movie.analyzer_data[self.name] = keywordlist

    def analyze_all(self, database):
        for movie in database.values():
            self.process_movie(movie)
