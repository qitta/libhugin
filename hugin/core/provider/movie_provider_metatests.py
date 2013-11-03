#!/usr/bin/env python
# encoding: utf-8

from hugin.core.provider.tmdb.tmdbmovie import TMDBMovie
from hugin.core.provider.ofdb.ofdbmovie import OFDBMovie
from hugin.core.provider.omdb.omdbmovie import OMDBMovie


PROVIDER = {

    TMDBMovie(): {
        'search': 'tmdb_search.json',
        'movie': 'tmdb_movie.json',
        'fail': 'tmdb_fail.json',
        'search_by_imdb': False
    },

    OFDBMovie(): {
        'search': 'ofdb_search.json',
        'movie': 'ofdb_movie.json',
        'fail': 'ofdb_fail.json',
        'search_by_imdb': True
    },

    OMDBMovie(): {
        'search': 'omdb_search.json',
        'movie': 'omdb_movie.json',
        'fail': 'omdb_fail.json',
        'search_by_imdb': True
    }
}


if __name__ == '__main__':
    import unittest

    class TestMovie(unittest.TestCase):

        def setUp(self):
            self._provider = [p for p in PROVIDER.keys()]
            self._params = {
                'title': 'Sin City',
                'year': '2005',
                'imdbid': 'tt0401792',
                'items': 5
            }

        def read_file(self, file_name):
            path = 'hugin/core/testdata/{0}'.format(file_name)
            with open(path, 'r') as f:
                return f.read()

        # static search tests, see :func: `core.provider.IProvider.search`
        # specs for further information
        def test_search_title(self):
            for provider in self._provider:
                self._params['year'] = self._params['imdbid'] = None
                result, finished = provider.search(self._params)
                self.assertFalse(finished)
                self.assertTrue(result is not None)

        def test_search_title_year(self):
            self._params['imdbid'] = None
            for provider in self._provider:
                result, finished = provider.search(self._params)
                self.assertFalse(finished)
                self.assertTrue(result is not None)

        def test_search_invalid_params(self):
            self._params = {key: None for key in self._params.keys()}
            for provider in self._provider:
                result, finished = provider.search(self._params)
                self.assertTrue(finished)
                self.assertTrue(result is None)

        def test_search_year_only(self):
            self._params = {key: None for key in self._params.keys()}
            for provider in self._provider:
                self._params['year'] = '2005'
                result, finished = provider.search(self._params)
                self.assertTrue(finished)
                self.assertTrue(result is None)

        def test_search_imdbid_only(self):
            self._params['items'] = self._params['title'] = None
            for provider in self._provider:
                result, finished = provider.search(self._params)
                if PROVIDER[provider]['search_by_imdb']:
                    self.assertFalse(finished)
                    self.assertTrue(result)
                else:
                    self.assertTrue(finished)
                    self.assertTrue(result is None)

        # static parse tests, see :func: `core.provider.IProvider.parse` specs
        # for further information
        def test_parse_search(self):
            for provider in self._provider:
                response = self.read_file(PROVIDER[provider]['search'])
                result, finished = provider.parse(
                    response,
                    self._params
                )
                self.assertTrue(result is not None)
                self.assertFalse(finished)

        def test_parse_movie(self):
            for provider in self._provider:
                response = self.read_file(PROVIDER[provider]['movie'])
                result, finished = provider.parse(
                    response,
                    self._params
                )
                self.assertTrue(isinstance(result, dict))
                self.assertTrue(finished)

        def test_parse_fail(self):
            for provider in self._provider:
                response = self.read_file(PROVIDER[provider]['fail'])
                result, finished = provider.parse(
                    response,
                    self._params
                )
                self.assertFalse(finished)
                self.assertTrue(result is None)

    unittest.main()
