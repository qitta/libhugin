#!/usr/bin/env python
# encoding: utf-8

"""
    OBSOLATE!
    Encapsulation for provider <-> url <-> request.
"""

from hugin.query import Query, QUERY_ATTRS
from collections import UserDict


class ProviderData(UserDict):
    def __init__(self, url=None, provider=None, query=None):
        self.data = {
            'url': url,
            'provider': provider,
            'query': query,
            'future': None,
            'response': None,
            'is_done': False,
            'result': None,
            'return_code': None,
            'retries_left': 5,
            'cache_used' : False
        }

    def invoke_build_url(self):
        """ Trigger the build url action of the provider. """
        self['url'] = self['provider'].build_url(self['query'])
        if self['url'] is None:
            self['is_done'] = True

    def invoke_parse_response(self):
        """ Trigger the parse url action of the provider. """
        self['result'], self['is_done'] = self['provider'].parse_response(
            self['response'], self['query']
        )
        self['previous_action'] = 'parse'

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

    def decrement_retries(self):
        if self['retries_left'] > 0:
            self['retries_left'] -= 1
        else:
            self['retries_left'] = 0
            self['is_done'] = True


#if __name__ == '__main__':
#    import unittest
#
#    URL = 'http://github.com'
#
#    # dummy provider to simulate provider response
#    class Provider:
#        def __init__(self, name):
#            self.name = name
#            self._value = 'success'
#
#        def parse_response(self, _dummy_response, _dummy_search_params):
#            _dummy_response, _dummy_search_params = None, None
#            result = {
#                'critical': (None, True),
#                'failed': (None, False),
#                'success': (['url'], False),
#                'success_nothing_found': ([], True)
#            }.get(self._value)
#            print(self._value, result)
#            return result
#
#        def build_url(self, _dummy_search_params):
#            _ = _dummy_search_params
#            len(_)
#            result = {
#                'failed': None,
#                'success': URL
#            }.get(self._value)
#            print(self._value, result)
#            return result
#
#        def set_state(self, state):
#            self._value = state
#
#        def retries_left(self):
#            return self['retries_left'] > 0
#
#        def decrement_retries(self):
#            self['retries_left'] -= 1
#
#    def create_query(**kwargs):
#        return Query(QUERY_ATTRS, kwargs)
#
#    def create_dummy_provider(name):
#        return Provider(name)
#
#    class TestProviderData(unittest.TestCase):
#        def setUp(self):
#            self._provider = create_dummy_provider('hans')
#            self._query = create_query(title='Sin City', type='movie')
#            self._provider_data = ProviderData(
#                provider=self._provider,
#                query=self._query
#            )
#
#        def test_providerdata_init(self):
#            self.assertTrue(self._provider_data.query is self._query)
#            self.assertFalse(self._provider_data.is_done)
#
#        def test_provider_build_url(self):
#            self._provider.set_state('success')
#            self._provider_data.invoke_build_url()
#            self.assertFalse(self._provider_data.is_done)
#            self.assertTrue(self._provider_data['url'] == URL)
#
#            self._provider.set_state('failed')
#            self._provider_data.invoke_build_url()
#            self.assertTrue(self._provider_data.is_done)
#            self.assertTrue(self._provider_data['url'] is None)
#
#        def test_provider_parse_response(self):
#            self._provider.set_state('success')
#            self._provider_data.invoke_parse_response()
#
#            self.assertFalse(self._provider_data.is_done)
#            self.assertTrue(self._provider_data.has_valid_result)
#
#            self._provider.set_state('success_nothing_found')
#            self._provider_data.invoke_parse_response()
#
#            self.assertTrue(self._provider_data.is_done)
#            self.assertTrue(self._provider_data.has_valid_result)
#
#            self._provider.set_state('failed')
#            for _ in range(4):
#                self._provider_data.invoke_parse_response()
#                self.assertFalse(self._provider_data.is_done)
#                self.assertFalse(self._provider_data.has_valid_result)
#            self._provider_data.invoke_parse_response()
#
#            self._provider.set_state('critical')
#            self._provider_data.invoke_parse_response()
#
#            self.assertTrue(self._provider_data.is_done)
#            self.assertFalse(self._provider_data.has_valid_result)
#
#    unittest.main()
