#!/usr/bin/env python
# encoding: utf-8

from collections import UserDict


class Query(UserDict):
    '''
    Simple query object
    '''
    def __init__(self, data):
        self._query_attrs = [
            'title', 'year', 'name', 'imdbid', 'type', 'search_text',
            'language', 'search_pictures', 'items', 'cache', 'retries',
            'strategy', 'providers'
        ]

        self.data = {key: None for key in self._query_attrs}
        self.data.update({
            'items': 1,
            'cache': True,
            'language': '',
            'retries': 5,
            'strategy': 'deep'
        })
        # self.data.update(data)
        for key, value in data.items():
            if key in self.data:
                self.data[key] = value

        def __getattr__(self, key):
            return self.data[key]


if __name__ == '__main__':
    def create_query(**kwargs):
        return Query(kwargs)
    q = create_query(wolfgang=223, title='Sin City', name='444')
    print(q)
