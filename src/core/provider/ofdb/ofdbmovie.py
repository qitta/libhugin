#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin
import core.provider as provider
from urllib.parse import urlencode


class OFDBMovie(provider.IMovieProvider):
    def __init__(self):
        print('__init__ ofdb Movie Provider.')
        self._base_url = 'http://ofdbgw.org/{path}/{query}'

    def search(self, title=None, year=None, imdbid=None):
        if imdbid:
            return self._base_url.format(path='imdb2ofdb_json', query=imdbid)
        else:
            return self._base_url.format(path='search_json', query=title)

    def parse(self, provider_data):
        r_json = provider_data.get('response').json()

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
