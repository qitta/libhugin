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
            'language', 'search_pictures', 'amount', 'cache', 'retries',
            'strategy', 'providers'
        ]

        self.data = {key: None for key in self._query_attrs}
        self.data.update({
            'amount': 1,
            'cache': True,
            'language': '',
            'retries': 5,
            'strategy': 'deep'
        })

        for key, value in data.items():
            if key in self.data:
                self.data[key] = value

    def __getattr__(self, key):
        return self.data[key]

    def _set_all_none(self):
        self.data = {key: None for key in self._query_attrs}



if __name__ == '__main__':
    def create_query(**kwargs):
        return Query(kwargs)
    q = create_query(title='Sin City')
    print(q)
