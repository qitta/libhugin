#!/usr/bin/env python
# encoding: utf-8

from guess_language import guess_language

# hugin
import hugin.analyze as plugin

class PlotLangIdentify(plugin.IAnalyzer):

    def process_movie(self, movie):
        lang = str(guess_language(movie.attributes.get('plot') or ''))
        movie.analyzer_data[self.name] = lang

    def process_database(self, database):
        for movie in database.values():
            self.process_movie(movie)
