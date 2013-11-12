#!/usr/bin/env python
# encoding: utf-8

""" Provider test module. """

from hugin.core.provider.tmdb.tmdbperson import TMDBPerson


PROVIDER = {

    TMDBPerson(): {
        'search': 'tmdb_person_search.json',
        'person': 'tmdb_person_response.json',
        'nothing_found': 'tmdb_nothing_found.json',
        'critical': 'tmdb_critical.json',
        'search_by_imdb': False
    }
}

if __name__ == '__main__':
    import unittest

    class TestMovie(unittest.TestCase):

        def setUp(self):
            self._providers = [p for p in PROVIDER.keys()]
            self._params = {
                'name': 'Emma Stone',
                'items': 5,
                'type': 'person',
                'language':'en'
            }

        def read_file(self, file_name):
            path = 'hugin/core/testdata/{0}'.format(file_name)
            with open(path, 'r') as f:
                return f.read()

        # static search tests, see :func: `core.provider.IProvider.search`
        # specs for further information
        def test_search_name(self):
            for provider in self._providers:
                result = provider.build_url(self._params)
                for item in result:
                    self.assertTrue(item is not None)
                    self.assertTrue(isinstance(item, list))

        def test_search_invalid_params(self):
            self._params = {key: None for key in self._params.keys()}
            for provider in self._providers:
                result = provider.build_url(self._params)
                self.assertTrue(result is None)
                self.assertTrue(result is None)

        #def test_search_year_only(self):
        #    self._params = {key: None for key in self._params.keys()}
        #    for provider in self._providers:
        #        self._params['year'] = '2005'
        #        result = provider.build_url(self._params)
        #        self.assertTrue(result is None)

        #def test_search_imdbid_only(self):
        #    self._params['items'] = self._params['title'] = None
        #    for provider in self._providers:
        #        result = provider.build_url(self._params)
        #        if PROVIDER[provider]['search_by_imdb']:
        #            self.assertTrue(result)
        #        else:
        #            self.assertTrue(result is None)

        ## static parse tests, see :func: `core.provider.IProvider.parse` specs
        ## for further information
        #def test_parse_build_url(self):
        #    for provider in self._providers:
        #        response = self.read_file(PROVIDER[provider]['search'])
        #        response = [('fakeurl', response)]
        #        result, finished = provider.parse_response(
        #            response,
        #            self._params
        #        )
        #        self.assertTrue(result is not None)
        #        self.assertFalse(finished)

        #def test_parse_movie(self):
        #    for provider in self._providers:
        #        response = self.read_file(PROVIDER[provider]['movie'])
        #        response = [('fakeurl', response)]
        #        result, finished = provider.parse_response(
        #            response,
        #            self._params
        #        )
        #        self.assertTrue(isinstance(result, dict))
        #        self.assertTrue(finished)

        #def test_parse_provider_no_results(self):
        #    for provider in self._providers:
        #        response = self.read_file(PROVIDER[provider]['nothing_found'])
        #        response = [('fakeurl', response)]
        #        result, finished = provider.parse_response(
        #            response,
        #            self._params
        #        )
        #        self.assertTrue(result == [])
        #        self.assertTrue(finished)

        #def test_parse_provider_critical(self):
        #    for provider in self._providers:
        #        response = self.read_file(PROVIDER[provider]['critical'])
        #        response = [('fakeurl', response)]
        #        result, finished = provider.parse_response(
        #            response,
        #            self._params
        #        )
        #        self.assertTrue(finished)
        #        self.assertTrue(result is None)

        #def test_parse_invalid(self):
        #    for provider in self._providers:
        #        result, finished = provider.parse_response(
        #            [('fakeurl', None)],
        #            self._params
        #        )
        #        self.assertTrue(finished)
        #        self.assertTrue(result is None)

    unittest.main()
