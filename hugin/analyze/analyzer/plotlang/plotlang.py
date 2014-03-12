#!/usr/bin/env python
# encoding: utf-8

from guess_language import guess_language

# hugin
import hugin.analyze as plugin


class PlotLangIdentify(plugin.IAnalyzer):

    def analyze(self, movie, attr_name='plot'):
        lang = str(guess_language(movie.attributes.get(attr_name) or ''))
        movie.analyzer_data[self.name] = lang

    def analyze_all(self, database):
        for movie in database.values():
            self.process_movie(movie)

    def parameters(self):
        return {
            'attr_name': str
        }
