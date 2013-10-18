#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin
from urllib.parse import urlencode
import core.provider as provider
import difflib


class OFDBMovie(provider.IMovieProvider):
    def __init__(self):
        print('__init__ ofdb Movie Provider.')
        self._base_url = 'http://ofdbgw.org/{path}/{query}'

    def search(self, search_params):
        if search_params['imdbid']:
            path, query = 'imdb2ofdb_json', search_params['imdbid']
        else:
            path, query = 'search_json', search_params['title']

        return self._base_url.format(path=path, query=query)

    def parse(self, response, search_params):
        ofdb_response = response.json().get('ofdbgw')
        status = ofdb_response['status']
        if status['rcode'] == 0:
            select_parse_method = {
                'movie': self._parse_movie_module,
                'imdb2ofdb': self._parse_imdb2ofdb_module,
                'search': self._parse_search_module
            }.get(status['modul'])

            if select_parse_method is not None:
                return select_parse_method(ofdb_response['resultat'], search_params)

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
                    self._string_similarity_ratio(
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

    def _string_similarity_ratio(self, s1, s2):
        return difflib.SequenceMatcher(None, s1.upper(), s2.upper()).ratio()

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
