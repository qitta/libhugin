#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin

__all__ = ['IMovieProvider', 'IPosterProvider', 'IBackdropProvider',
           'IPlotProvider', 'IPersonProvider', 'IOutputConverter',
           'IPostprocessing', 'IProvider']


class IProvider(IPlugin):
    pass


class IMovieProvider(IProvider):
    pass


class IPosterProvider(IProvider):
    pass

    def search(self, search_params):
        return 'Not implemented yet.'

    def parse(self, result, search_params):
        return 'Not implemented yet.'


class IBackdropProvider(IProvider):
    pass


class IPlotProvider(IProvider):
    pass


class IPersonProvider(IProvider):
    pass


class IOutputConverter(IPlugin):
    pass


class IPostprocessing(IPlugin):
    pass
