#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin
import core.provider as provider
from urllib.parse import urlencode


class OMDBMovie(provider.IMovieProvider):
    name = __name__

    def __init__(self):
        print('__init__ OMDB Movie Provider.')
        self._base_url = 'http://www.omdbapi.com/?{query}'

    def search(self, title='', year='', imdbid=''):
        params = {'s': title, 'y': year, 'i': imdbid, 'r': 'json'}
        return self._base_url.format(query=urlencode(params))

    def parse(self, content_json):
        pass

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', self.__class__.name)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
