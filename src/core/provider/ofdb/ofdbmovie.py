#!/usr/bin/env python
# encoding: utf-8


from common.utils.provider import string_similarity_ratio
from yapsy.IPlugin import IPlugin
import core.provider as provider
import json


class OFDBMovie(provider.IMovieProvider):
    def __init__(self):
        print('__init__ ofdb Movie Provider.')
        self._base_url = 'http://ofdbgw.org/{path}/{query}'

    def search(self, search_params):
        if search_params['imdbid']:
            path, query = 'imdb2ofdb_json', search_params['imdbid']
        else:
            path, query = 'search_json', search_params['title']

        return (self._base_url.format(path=path, query=query), False)

    def parse(self, response, search_params):
        ofdb_response = json.loads(response).get('ofdbgw')
        status = ofdb_response['status']
        print('Status:', status)
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

    def _parse_imdb2ofdb_module(self, result, _):
        return self._build_movie_url([result['ofdbid']])

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

        # sort by ratio, generate ofdbid list with requestet item count
        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])

        matches = [item['ofdbid'] for item in similarity_map[:item_count]]
        return self._build_movie_url(matches)

    def _parse_movie_module(self, result, _):
        print(result['titel'])

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
    from core.providerhandler import create_provider_data
    import unittest

    class TestOFDBMovie(unittest.TestCase):

        def setUp(self):
            self._pd = create_provider_data()
            self._ofdb = OFDBMovie()
            with open('core/tmp/ofdb_response.json', 'r') as f:
                self._ofdb_response_fail = f.read()

            with open('core/tmp/ofdb_response_fail.json', 'r') as f:
                self._ofdb_response = f.read()

        def test_search_title(self):
            params = {'title': 'Sin City', 'imdbid': None}
            url = 'http://ofdbgw.org/search_json/Sin City'
            self.assertTrue(self._ofdb.search(params), url)

        def test_search_title_imdbid(self):
            params = {'title': 'Sin City', 'imdbid': 'tt2389238'}
            url = 'http://ofdbgw.org/imdb2ofdb_json/tt2389238'
            self.assertTrue(self._ofdb.search(params), url)

        def test_search_imdbid_only(self):
            params = {'title': None, 'imdbid': 'tt2389238'}
            url = 'http://ofdbgw.org/imdb2ofdb_json/tt2389238'
            self.assertTrue(self._ofdb.search(params), url)

        def test_parse_response(self):
            params = {'title': 'Sin City', 'imdbid': None, 'items': 5}
            r = self._ofdb.parse(self._ofdb_response, params)
            print(r)

        def test_parse_response_fail(self):
            params = {'title': 'Sin City', 'imdbid': None, 'items': 5}
            r = self._ofdb.parse(self._ofdb_response_fail, params)
            print(r)

    unittest.main()
