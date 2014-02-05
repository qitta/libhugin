#!/usr/bin/env python
# encoding: utf-8

from yapsy.IPlugin import IPlugin


class IModifier(IPlugin):

    def process_movie(self, movie):
        pass

    def process_database(self, database):
        pass

class IAnalyzer(IPlugin):

    def process_movie(self, movie):
        pass

    def process_database(self, database):
        pass

class IComparator(IPlugin):

    def process(self, movie_a, movie_b):
        pass
