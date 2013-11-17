#!/usr/bin/env python
# encoding: utf-8

from collections import UserDict

#query attrs for testing purposes, Session itself contains query attrs
QUERY_ATTRS = [
    'title', 'year', 'name', 'imdbid', 'type', 'search_text',
    'language', 'seach_picture', 'items', 'use_cache'
]


class Query(UserDict):
    '''
    Simple query object
    '''
    def __init__(self, query_attrs, data):
        self._query_attrs = query_attrs
        self.data = {k: None for k in self._query_attrs}
        self._set_query_values(data)
        self._set_required_defaults()

    def _set_query_values(self, data):
        '''
        Filters all unwanted query params
        '''
        for key, value in data.items():
            if key in self.data:
                self.data[key] = value

    def _set_required_defaults(self):
        if self.data['items'] is None:
            self.data['items'] = 1
        if self.data['use_cache'] is None:
            self.data['use_cache'] = True
        if self.data['language'] is None:
            self.data['language'] = 'en'


if __name__ == '__main__':
    def create_query(**kwargs):
        return Query(QUERY_ATTRS, kwargs)
    q = create_query(wolfgang=223, title='Sin City', name='444')
    print(q)
