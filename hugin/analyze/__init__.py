#!/usr/bin/env python
# encoding: utf-8

from yapsy.IPlugin import IPlugin


class IModifier(IPlugin):

    def modify(self, movie):
        pass

    def modify_all(self, database):
        pass


class IAnalyzer(IPlugin):

    def analyze(self, movie):
        pass

    def analyze_all(self, database):
        pass


class IComparator(IPlugin):

    def compare(self, movie_a, movie_b):
        pass

    def compare_all(self, database):
        pass
