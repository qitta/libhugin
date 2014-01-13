#!/usr/bin/env python
# encoding: utf-8

from hugin.analyze.rake import extract_keywords
# hugin
import hugin.analyze as plugin

class KeywordExtractor(plugin.IAnalyzer):

    def process_movie(self, movie, score_threshold=1.0):
        if movie.attributes.get('plot'):
            lang, keywords = extract_keywords(
                movie.attributes.get('plot'), use_stemmer=False
            )
            keywordlist = []
            for keyword, score in keywords.items():
                if score > score_threshold:
                    keywordlist.append(list(keyword))
            movie.analyzer_data[self.name] = keywordlist


    def process_database(self, database):
        for movie in database.values():
            self.process_movie(movie)
