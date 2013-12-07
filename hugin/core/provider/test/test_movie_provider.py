#!/usr/bin/env python
# encoding: utf-8

""" Provider test module. """

from hugin.core.provider.tmdb.tmdbmovie import TMDBMovie
from hugin.core.provider.ofdb.ofdbmovie import OFDBMovie
from hugin.core.provider.omdb.omdbmovie import OMDBMovie


PROVIDER = {

    TMDBMovie(): {
        'name': 'tmdb',
        'search': 'tmdb_movie_search.json',
        'movie': 'tmdb_movie_response.json',
        'nothing_found': 'tmdb_nothing_found.json',
        'critical': 'tmdb_critical.json',
        'search_by_imdb': True
    },

    OFDBMovie(): {
        'name': 'ofdb',
        'search': 'ofdb_movie_search.json',
        'movie': 'ofdb_movie_response.json',
        'nothing_found': 'ofdb_nothing_found.json',
        'critical': 'ofdb_critical.json',
        'search_by_imdb': True
    },

    OMDBMovie(): {
        'name': 'omdb',
        'search': 'omdb_movie_search.json',
        'movie': 'omdb_movie_response.json',
        'nothing_found': 'omdb_nothing_found.json',
        'critical': 'omdb_critical.json',
        'search_by_imdb': True
    }
}


if __name__ == '__main__':
    import unittest
    from hugin.query import Query

    class TestMovie(unittest.TestCase):

        def setUp(self):
            self._providers = [p for p in PROVIDER.keys()]
            self._params = Query({
                'title': 'Sin City',
                'year': '2005',
                'imdbid': 'tt0401792',
                'amount': 2,
                'type': 'movie',
                'search_pictures': True,
                'language': 'en'
            })

            self._key_types = {
                'title': str,
                'original_title': str,
                'plot': str,
                'runtime': int,
                'imdbid': str,
                'vote_count': int,
                'rating': str,
                'providerid': str,
                'alternative_titles': list,
                'directors': list,
                'writers': list,
                'crew': list,
                'year': int,
                'poster': list,
                'fanart': list,
                'countries': list,
                'genre': list,
                'genre_norm': list,
                'collection': list,
                'studios': list,
                'trailers': list,
                'actors': list,
                'keywords': list,
                'tagline': str,
                'outline': str
            }

        def read_file(self, file_name):
            path = 'hugin/core/testdata/{0}'.format(file_name)
            with open(path, 'r') as f:
                return f.read()

        # static search tests, see :func: `core.provider.IProvider.search`
        # specs for further information
        def test_search_title(self):
            for provider in self._providers:
                self._params.year = self._params.imdbid = None
                result_list = provider.build_url(self._params)
                self.assertTrue(isinstance(result_list, list))
                for result in result_list:
                    self.assertTrue(isinstance(result, str))
                    self.assertTrue(result is not None)

        def test_search_title_year(self):
            self._params.imdbid = None
            for provider in self._providers:
                result_list = provider.build_url(self._params)
                self.assertTrue(isinstance(result_list, list))
                for result in result_list:
                    self.assertTrue(isinstance(result, str))
                    self.assertTrue(result is not None)

        def test_search_invalid_params(self):
            self._params._set_all_none()

            for provider in self._providers:
                result_list = provider.build_url(self._params)
                self.assertTrue(result_list is None)

        def test_search_year_only(self):
            self._params._set_all_none()
            for provider in self._providers:
                self._params.year = '2005'
                result_list = provider.build_url(self._params)
                self.assertTrue(result_list is None)

        def test_search_imdbid_only(self):
            self._params.amount = self._params.title = None
            for provider in self._providers:
                result_list = provider.build_url(self._params)
                self.assertTrue(isinstance(result_list, list))
                if PROVIDER[provider]['search_by_imdb']:
                    for result in result_list:
                        #self.assertTrue(isinstance(result, str))
                        self.assertTrue(result is not None)
                else:
                    self.assertTrue(result is None)

        ## static parse tests, see :func: `core.provider.IProvider.parse` specs
        ## for further information
        def test_parse_search_response(self):
            """
            We expect a list of lists on a valid parse.

            Provider which needs multiple requests to get a complete result:
            ([[url_images_movie1, url_cast_movie1], [...movie2...]], False)

            Provider which needs just a single request:
            ([[url_movie_1], [url_movie_2]], False)

            """
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['search'])
                response = [('fakeurl/search/movie?', response)]
                result_list, finished = provider.parse_response(
                    response,
                    self._params
                )
                self.assertTrue(isinstance(result_list, list))
                for result in result_list:
                    self.assertTrue(isinstance(result, list))
                    for item in result:
                        self.assertTrue(isinstance(item, str))
                        self.assertTrue(item is not None)
                    self.assertTrue(result is not None)
                    self.assertFalse(finished)

        def test_parse_movie(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['movie'])
                response = [('fakeurl/movie/', response)]
                result, finished = provider.parse_response(
                    response,
                    self._params
                )
                self.assertTrue(isinstance(result, dict))
                self.assertTrue(finished)

        def test_parse_movie_result_dict(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['movie'])
                response = [('fakeurl/movie/', response)]
                result_dict, finished = provider.parse_response(
                    response,
                    self._params
                )
                self.assertTrue(isinstance(result_dict, dict))
                for key, value in result_dict.items():
                    if value:
                        self.assertTrue(isinstance(value, self._key_types[key]))


        def test_parse_provider_no_results(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['nothing_found'])
                response = [('search/movie?', response)]
                result_list, finished = provider.parse_response(
                    response,
                    self._params
                )
                self.assertTrue(isinstance(result_list, list))
                for result in result_list:
                    self.assertTrue(result == [])
                self.assertTrue(finished)

        def test_parse_provider_critical(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['critical'])
                response = [('fakeurl', response)]
                result_list, finished = provider.parse_response(
                    response,
                    self._params
                )
                self.assertTrue(finished)
                self.assertTrue(result_list is None)

        def test_parse_invalid(self):
            for provider in self._providers:
                result_list, finished = provider.parse_response(
                    [('fakeurl', None)],
                    self._params
                )
                self.assertTrue(finished)
                self.assertTrue(result_list is None)

    unittest.main()
