#!/usr/bin/env python
# encoding: utf-8

from hugin.common.utils.stringcompare import string_similarity_ratio
import hugin.core.provider as provider
from urllib.parse import quote
import json


class OFDBMovie(provider.IMovieProvider):
    def __init__(self):
        self._base_url = 'http://ofdbgw.org/{path}/{query}'

    def search(self, search_params):
        # not enough search params
        if search_params['title'] is None and search_params['imdbid'] is None:
            return (None, True)

        # try to search by imdbid if available, else use title
        if search_params['imdbid']:
            path, query = 'imdb2ofdb_json', search_params['imdbid']
        else:
            path, query = 'search_json', quote(search_params['title'])
        return (self._base_url.format(path=path, query=query), False)

    def parse(self, response, search_params):
        ofdb_response = json.loads(response).get('ofdbgw')
        status = ofdb_response['status']
        if status['rcode'] == 4:
            return ([], True)

        if status['rcode'] == 0:
            select_parse_method = {
                'movie': self._parse_movie_module,
                'imdb2ofdb': self._parse_imdb2ofdb_module,
                'search': self._parse_search_module
            }.get(status['modul'])

            if select_parse_method is not None:
                return select_parse_method(
                    ofdb_response['resultat'],
                    search_params
                )
        else:
            return (None, False)

    def _parse_imdb2ofdb_module(self, result, _):
        return (self._build_movie_url([result['ofdbid']]), False)

    def _parse_search_module(self, result, search_params):
        # create similarity matrix for title, check agains german and original
        # title, higher ratio wins
        similarity_map = []
        for result in result['eintrag']:
            # Get the title with the highest similarity ratio:
            ratio = 0.0
            for title_key in ['titel_de', 'titel_orig']:
                ratio = max(
                    ratio,
                    string_similarity_ratio(
                        result[title_key],
                        search_params['title']
                    )
                )
            similarity_map.append({'ofdbid': result['id'], 'ratio': ratio})

        print(similarity_map)
        # sort by ratio, generate ofdbid list with requestet item count
        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])

        matches = [item['ofdbid'] for item in similarity_map[:item_count]]
        return (self._build_movie_url(matches), False)

    def _parse_movie_module(self, result, _):
        result = {
            'title': result['titel'],
            'year': result['jahr'],
            'imdbid': result['imdbid'],
        }
        return (result, True)

    def _build_movie_url(self, ofdbid_list):
        url_list = []
        for ofdbid in ofdbid_list:
            url_list.append(
                self._base_url.format(path='movie_json', query=ofdbid)
            )
        return url_list

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)


if __name__ == '__main__':
    from hugin.core.providerhandler import create_provider_data
    from hugin.common.utils.testing_dummies import create_search_params_dummy
    import unittest

    class TestOFDBMovie(unittest.TestCase):

        def setUp(self):
            self._pd = create_provider_data()
            self._ofdb = OFDBMovie()

            # creates a dummy with title sin city, year 2005, imdbid tt0401792
            # and item count 5
            self._params = create_search_params_dummy()

            self._matches = [
                'http://ofdbgw.org/movie_json/72886',
                'http://ofdbgw.org/movie_json/181754',
                'http://ofdbgw.org/movie_json/16429',
                'http://ofdbgw.org/movie_json/157214',
                'http://ofdbgw.org/movie_json/85240'
            ]
            with open('hugin/core/testdata/ofdb_response_fail.json', 'r') as f:
                self._ofdb_response_fail = f.read()

            with open('hugin/core/testdata/ofdb_response_movie.json', 'r') as f:
                self._ofdb_response_movie = f.read()

            with open('hugin/core/testdata/ofdb_response.json', 'r') as f:
                self._ofdb_response = f.read()

        # static search tests, see :func: `core.provider.IProvider.search`
        # specs for further information
        def test_search_title(self):
            self._params['imdbid'] = self._params['items'] = None
            result, finished = self._ofdb.search(self._params)
            self.assertFalse(finished)
            self.assertTrue(result.endswith('Sin%20City'))

        def test_search_title_imdbid(self):
            self._params['items'] = None
            result, finished = self._ofdb.search(self._params)
            self.assertFalse(finished)
            self.assertTrue('Sin%20City' not in result)
            self.assertTrue('2005' not in result)
            self.assertTrue('tt0401792' in result)

        def test_search_imdbid_only(self):
            self._params['items'] = self._params['title'] = None
            result, finished = self._ofdb.search(self._params)
            self.assertFalse(finished)
            self.assertTrue('tt0401792' in result)

        def test_search_invalid_params(self):
            self._params = {key: None for key in self._params.keys()}
            result, finished = self._ofdb.search(self._params)
            self.assertTrue(finished)
            self.assertTrue(result is None)

        # static parse tests, see :func: `core.provider.IProvider.parse` specs
        # for further information
        def test_parse_response_fail(self):
            result, finished = self._ofdb.parse(
                self._ofdb_response_fail,
                self._params
            )
            self.assertFalse(finished)
            self.assertTrue(result is None)

        def test_parse_response(self):
            result, finished = self._ofdb.parse(
                self._ofdb_response,
                self._params
            )
            self.assertFalse(finished)
            for item in result:
                self.assertTrue(item in self._matches)

        def test_parse_movie(self):
            result, finished = self._ofdb.parse(
                self._ofdb_response_movie,
                self._params
            )
            self.assertTrue(isinstance(result, dict))
            self.assertTrue(finished)

    unittest.main()
