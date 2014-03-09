#!/usr/bin/env python
# encoding: utf-8

# hugin
import hugin.analyze as plugin
import re


class PlotCleaner(plugin.IModifier):

    def process_movie(self, movie, attr_name='plot'):
        plot = movie.attributes.get(attr_name)
        if plot:
            movie.attributes[attr_name] = re.sub(
                '\s+\(.*?\)(\s*)', '\g<1>', plot
            )

    def process_database(self, db):
        for movie in db.values():
            self.movie(movie)
