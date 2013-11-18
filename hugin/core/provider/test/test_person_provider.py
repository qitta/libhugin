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
                'language': 'en',
                'items': 3
            }

        def read_file(self, file_name):
            path = 'hugin/core/testdata/{0}'.format(file_name)
            with open(path, 'r') as f:
                return f.read()

        # static search tests, see :func: `core.provider.IProvider.search`
        # specs for further information
        def test_search_name(self):
            for provider in self._providers:
                result_list = provider.build_url(self._params)
                self.assertTrue(isinstance(result_list, list))
                for result in result_list:
                    self.assertTrue(result is not None)
                    self.assertTrue(isinstance(result, str))

        def test_search_invalid_params(self):
            self._params = {key: None for key in self._params.keys()}
            for provider in self._providers:
                result = provider.build_url(self._params)
                self.assertTrue(result is None)

        # static parse tests, see :func: `core.provider.IProvider.parse` specs
        # for further information
        def test_parse_build_url(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['search'])
                response = [('fakeurl/search/person?', response)]
                result_list, finished = provider.parse_response(
                    response,
                    self._params
                )
                self.assertTrue(isinstance(result_list, list))
                for result in result_list:
                    self.assertTrue(isinstance(result, list))
                    self.assertTrue(result is not None)
                    for item in result:
                        self.assertTrue(isinstance(item, str))
                        self.assertTrue(item is not None)
                    self.assertFalse(finished)

        def test_parse_person(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['person'])
                response = [('fakeurl/person/', response)]
                result_list, finished = provider.parse_response(
                    response,
                    self._params
                )
                self.assertTrue(isinstance(result_list, list))
                for result in result_list:
                    self.assertTrue(isinstance(result, dict))
                self.assertTrue(finished)

        def test_parse_provider_no_results(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['nothing_found'])
                response = [('fakeurl/search/person?', response)]
                result_list, finished = provider.parse_response(
                    response,
                    self._params
                )
                for result in result_list:
                    self.assertTrue(result == [])
                    self.assertTrue(finished)

        def test_parse_provider_critical(self):
            for provider in self._providers:
                response = self.read_file(PROVIDER[provider]['critical'])
                response = [('fakeurl/person?88', response)]
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
