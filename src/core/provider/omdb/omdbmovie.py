#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin
import core.provider as provider
from urllib.parse import urlencode


class OMDBMovie(provider.IMovieProvider):
    def __init__(self):
        print('__init__ OMDB Movie Provider.')
        self._base_url = 'http://www.omdbapi.com/?{query}'

    def search(self, title='', year='', imdbid=''):
        params = {'s': title, 'y': year, 'i': imdbid}
        return self._base_url.format(query=urlencode(params))

    def parse(self, provider_data):
        r_json = provider_data.get('response').json()

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
