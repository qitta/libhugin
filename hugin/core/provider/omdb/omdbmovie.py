#!/usr/bin/env python
# encoding: utf-8


from hugin.common.utils.stringcompare import string_similarity_ratio
from yapsy.IPlugin import IPlugin
from urllib.parse import urlencode
import hugin.core.provider as provider
import json


class OMDBMovie(provider.IMovieProvider):
    name = __name__

    def __init__(self):
        self._base_url = 'http://www.omdbapi.com/?{query}'

    def search(self, search_params):
        if search_params['imdbid']:
            params = {
                'i': search_params['imdbid']
            }
        else:
            params = {
                's': search_params['title'] or '',
                'y': search_params['year'] or ''
            }
        return (self._base_url.format(query=urlencode(params)), False)

    def parse(self, response, search_params):
        try:
            response = json.loads(response)
        except ValueError as v:
            return (None, False)
        else:
            if 'Error' in response:
                return (None, False)
            if 'Search' in response:
                return self._parse_search_module(response, search_params)

            return self._parse_movie_module(response, search_params)

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['Search']:
            ratio = (
                string_similarity_ratio(
                    result['Title'],
                    search_params['title']
                )
            )
            similarity_map.append({'imdbid': result['imdbID'], 'ratio': ratio})

        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])
        matches = [item['imdbid'] for item in similarity_map[:item_count]]
        return (self._build_movie_url(matches), False)

    def _build_movie_url(self, matches):
        url_list = []
        for item in matches:
            query = 'i={imdb_id}'.format(imdb_id=item)
            url_list.append(
                self._base_url.format(query=query)
            )
        return url_list

    def _parse_movie_module(self, data, search_params):
        result = {
            'title': data['Title'],
            'year': data['Year'],
            'imdbid': data['imdbID'],
        }
        return (result, True)

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', self.__class__.name)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)


if __name__ == '__main__':
    from hugin.core.providerhandler import create_provider_data
    import unittest

    class TestOMDBMovie(unittest.TestCase):

        def setUp(self):
            self._pd = create_provider_data()
            self._omdb = OMDBMovie()
            self._params = {
                'title': 'Sin City',
                'year': '2005',
                'imdbid': 'tt0401792',
                'items': 5
            }
            with open('hugin/core/testdata/omdb_response_fail.json', 'r') as f:
                self._omdb_response_fail = f.read()

            with open('hugin/core/testdata/omdb_response_movie.json', 'r') as f:
                self._omdb_response_movie = f.read()

            with open('hugin/core/testdata/omdb_response_search.json', 'r') as f:
                self._omdb_response = f.read()

        def _init_with_none(self, params):
            return {key: None for key in params.keys()}

        # static search tests, see :func: `core.provider.IProvider.search`
        # specs for further information
        def test_search_title(self):
            self._params['imdbid'] = self._params['items'] = None
            self._params['year'] = None
            result, finished = self._omdb.search(self._params)
            self.assertFalse(finished)

        def test_search_title_year(self):
            self._params['imdbid'] = self._params['items'] = None
            result, finished = self._omdb.search(self._params)
            self.assertFalse(finished)

        def test_search_title_imdbid(self):
            self._params['items'] = None
            result, finished = self._omdb.search(self._params)
            self.assertFalse(finished)

        def test_search_imdbid_only(self):
            self._params['items'] = self._params['title'] = None
            result, finished = self._omdb.search(self._params)
            self.assertFalse(finished)

        # static parse tests, see :func: `core.provider.IProvider.parse` specs
        # for further information
        def test_parse_response(self):
            result, finished = self._omdb.parse(
                self._omdb_response,
                self._params
            )
            self.assertFalse(finished)

        def test_parse_response_fail(self):
            result, finished = self._omdb.parse(
                self._omdb_response_fail,
                self._params
            )
            self.assertFalse(finished)
            self.assertTrue(result is None)

        def test_parse_movie(self):
            result, finished = self._omdb.parse(
                self._omdb_response_movie,
                self._params
            )
            self.assertTrue(finished)
            self.assertTrue(isinstance(result, dict))

    unittest.main()
