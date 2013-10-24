#!/usr/bin/env python
# encoding: utf-8


from common.utils.provider import string_similarity_ratio
from yapsy.IPlugin import IPlugin
from urllib.parse import quote
import core.provider as provider
import json

#api.themoviedb.org/3/movie/550?api_key=ff9d65f1e39e8a239124b7e098001a57


class TMDBMovie(provider.IMovieProvider):
    name = __name__

    def __init__(self):
        self._api_key = '?api_key=ff9d65f1e39e8a239124b7e098001a57'
        self._base_url = 'http://api.themoviedb.org/3/{path}{apikey}{query}'

    def search(self, search_params):
        if search_params['title']:
            path = 'search/movie'
            title = quote(search_params['title'])
            query = '&query={value}'.format(value=title)
            return (
                self._base_url.format(
                    path=path,
                    apikey=self._api_key,
                    query=query
                ),
                False
            )
        else:
            return ([], False)

    def parse(self, response, search_params):
        tmdb_response = json.loads(response)
        if 'total_results' in tmdb_response:
            if tmdb_response['total_results'] == 0:
                return ([], True)
            else:
                print('...searching movie')
                return self._parse_search_module(tmdb_response, search_params)
        elif 'adult' in tmdb_response:
            print('...parsing movie')
            return self._parse_movie_module(tmdb_response, search_params)
        else:
            return (None, False)

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['results']:
            ratio = 0.0
            for title_key in ['original_title', 'title']:
                ratio = max(
                    ratio,
                    string_similarity_ratio(
                        result[title_key],
                        search_params['title']
                    )
                )
            similarity_map.append({'tmdbid': result['id'], 'ratio': ratio})

        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])
        matches = [item['tmdbid'] for item in similarity_map[:item_count]]
        return (self._build_movie_url(matches), False)

    def _build_movie_url(self, matches):
        url_list = []
        for tmdbid in matches:
            path = 'movie/{tmdbid}'.format(tmdbid=tmdbid)
            url_list.append(
                self._base_url.format(
                    path=path,
                    apikey=self._api_key,
                    query='&language=de'
                )
            )
        return url_list

    def _parse_movie_module(self, data, search_params):
        result = {
            'title': data['title'],
            'year': data['release_date'][:4],
            'imdbid': data['imdb_id'],
        }
        return (result, True)

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', self.__class__.name)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)


if __name__ == '__main__':
    from core.providerhandler import create_provider_data
    import unittest

    class TestOMDBMovie(unittest.TestCase):

        def setUp(self):
            self._pd = create_provider_data()
            self._tmdb = TMDBMovie()
            self._params = {
                'title': 'Sin City',
                'year': '2005',
                'imdbid': 'tt0401792',
                'items': 5
            }
            with open('core/tmp/tmdb_response_search.json', 'r') as f:
                self._tmdb_response_movie_search = f.read()

            with open('core/tmp/tmdb_response_movie.json', 'r') as f:
                self._tmdb_response_movie = f.read()

        def test_search(self):
            r = self._tmdb.search(self._params)

        def test_parse(self):
            r = self._tmdb.parse(
                self._tmdb_response_movie_search,
                self._params
            )

        def test_parse_movie(self):
            r = self._tmdb.parse(
                self._tmdb_response_movie,
                self._params
            )
            import pprint
            pprint.pprint(r)

    unittest.main()
