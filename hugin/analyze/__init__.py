#!/usr/bin/env python
# encoding: utf-8

from yapsy.IPlugin import IPlugin


class IModifier(IPlugin):

    def modify(self, movie, **kwargs):
        pass

    def modify_all(self, database, **kwargs):
        pass

    def parameters(self):
        return {}


class IAnalyzer(IPlugin):

    def analyze(self, movie, **kwargs):
        pass

    def analyze_all(self, database, **kwargs):
        pass

    def parameters(self):
        return {}


class IComparator(IPlugin):

    def compare(self, movie_a, movie_b, **kwargs):
        pass

    def compare_all(self, database, **kwargs):
        pass

    def parameters(self):
        return {}
