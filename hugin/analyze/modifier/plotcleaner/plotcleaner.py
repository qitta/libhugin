#!/usr/bin/env python
# encoding: utf-8

# hugin
import hugin.analyze as plugin
import re


class PlotCleaner(plugin.IModifier):

    def __init__(self):
        self._pattern = '\s+\(.*?\)(\s*)'

    def process_movie(self, movie):
        plot = movie.attributes.get('plot')
        if plot:
            movie.attributes['plot'] = re.sub(self._pattern, '\g<1>', plot)

    def process_database(self, db):
        for movie in db.values():
            self.movie(movie)
