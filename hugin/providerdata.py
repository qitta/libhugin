#!/usr/bin/env python
# encoding: utf-8

from collections import UserDict
from hugin.query import Query, QUERY_ATTRS


class ProviderData(UserDict):
    def __init__(self, url=None, provider=None, query=None):
        self.data = {
            'url': url,
            'provider': provider,
            'query': query,
            'response': None,
            'is_done': False,
            'result': None,
            'return_code': None,
            'retries_left': 5,
            'job_id': id(query)
        }

    def search(self):
        self['url'] = self['provider'].search(self['query'])
        if self['url'] is None:
            self['retries_left'] = 0
            self['is_done'] = True

    def parse(self):
        self['result'], self['is_done'] = self['provider'].parse(
            self['response'], self['query']
        )
        if self['is_done'] is True and self['result'] is None:
            self['retries_left'] = 0
        elif self['is_done'] is False and self['result'] is None:
            self['retries_left'] -= 1

    def __repr__(self):
        return 'Provider: ' + str(self['provider']) + str(self['result'])

    @property
    def query(self):
        return self['query']

    @property
    def is_done(self):
        return self['is_done']

    @property
    def has_valid_result(self):
        return self['result'] is not None

    @property
    def retries_left(self):
        return self['retries_left'] > 0

    def dec_retries(self):
        self['retries_left'] -= 1


if __name__ == '__main__':
    import unittest

    URL = 'http://github.com'

    # dummy provider to simulate provider response
    class Provider:
        def __init__(self, name):
            self.name = name
            self._value = 'success'

        def parse(self, _dummy_response, _dummy_search_params):
            _dummy_response, _dummy_search_params = None, None
            result = {
                'critical': (None, True),
                'failed': (None, False),
                'success': (['url'], False),
                'success_nothing_found': ([], True)
            }.get(self._value)
            print(self._value, result)
            return result

        def search(self, _dummy_search_params):
            _ = _dummy_search_params
            len(_)
            result = {
                'failed': None,
                'success': URL
            }.get(self._value)
            print(self._value, result)
            return result

        def set_state(self, state):
            self._value = state

    def create_query(**kwargs):
        return Query(QUERY_ATTRS, kwargs)

    def create_dummy_provider(name):
        return Provider(name)

    class TestProviderData(unittest.TestCase):
        def setUp(self):
            self._provider = create_dummy_provider('hans')
            self._url = 'http://github.com'
            self._query = create_query(title='Sin City', type='movie')
            self._provider_data = ProviderData(
                provider=self._provider,
                query=self._query
            )

        def test_providerdata_init(self):
            self.assertTrue(self._provider_data.query is self._query)
            self.assertFalse(self._provider_data.is_done)

        def test_provider_search(self):
            self._provider.set_state('success')
            self._provider_data.search()
            self.assertFalse(self._provider_data.is_done)
            self.assertTrue(self._provider_data['url'] == URL)
            self.assertTrue(self._provider_data.retries_left)

            self._provider.set_state('failed')
            self._provider_data.search()
            self.assertTrue(self._provider_data.is_done)
            self.assertTrue(self._provider_data['url'] is None)
            self.assertFalse(self._provider_data.retries_left)

        def test_provider_parse(self):
            self._provider.set_state('success')
            self._provider_data.parse()

            self.assertFalse(self._provider_data.is_done)
            self.assertTrue(self._provider_data.has_valid_result)
            self.assertTrue(self._provider_data.retries_left)

            self._provider.set_state('success_nothing_found')
            self._provider_data.parse()

            self.assertTrue(self._provider_data.is_done)
            self.assertTrue(self._provider_data.has_valid_result)
            self.assertTrue(self._provider_data.retries_left)

            self._provider.set_state('failed')
            for _ in range(4):
                self._provider_data.parse()
                self.assertFalse(self._provider_data.is_done)
                self.assertFalse(self._provider_data.has_valid_result)
                self.assertTrue(self._provider_data.retries_left)
            self._provider_data.parse()
            self.assertFalse(self._provider_data.retries_left)

            self._provider.set_state('critical')
            self._provider_data.parse()

            self.assertTrue(self._provider_data.is_done)
            self.assertFalse(self._provider_data.has_valid_result)
            self.assertFalse(self._provider_data.retries_left)


    unittest.main()
