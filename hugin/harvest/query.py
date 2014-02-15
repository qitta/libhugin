#!/usr/bin/env python
# encoding: utf-8

from collections import UserDict


class Query(UserDict):
    """
    Represents a search query that is passed to the harvest submit method.

    """
    def __init__(self, user_data):
        self._query_attrs = [
            'title', 'year', 'name', 'imdbid', 'type', 'language', 'search',
            'amount', 'cache', 'retries', 'strategy', 'providers',
            'fuzzysearch', 'id_title_lookup'
        ]

        self.data = {key: None for key in self._query_attrs}
        self.data.update({
            'amount': 3,
            'cache': True,
            'search': 'both',
            'remove_invalid': True,
            'language': '',
            'retries': 5,
            'fuzzysearch': False,
            'strategy': 'flat',
            'id_title_lookup': False
        })

        self._check_params_contradictory(user_data)

        for key, value in user_data.items():
            if key in self.data and value:
                self.data[key] = value

        self._cleanup_params()

    def _cleanup_params(self):
        if self.data['type'] == 'movie':
            self.data.pop('name', None)
        else:
            self.data.pop('title', None)
            self.data.pop('year', None)
            self.data.pop('imdbid', None)

    def _check_params_contradictory(self, data):
        movie_params = data.get('title') or data.get('imdbid')

        if all([movie_params, data.get('name')]):
            raise KeyError('You can only search for title/imdbid *or* name.')

        if not any([movie_params, data.get('name')]):
            raise KeyError('You need to search for title, imdbid or name')

        if not data.get('type'):
            if 'title' in data or 'imdbid' in data:
                data.setdefault('type', 'movie')
            else:
                data.setdefault('type', 'person')

        if data['type'] not in ['movie', 'person']:
            raise KeyError('Invalid metadata type {0}'.format(data['type']))

        if all([movie_params, data['type'] == 'person']):
            raise KeyError('Params and metadatatype dosent match.')

        if all([data.get('name'), data['type'] == 'movie']):
            raise KeyError('Params and metadatatype dosent match.')

    def __getattr__(self, key):
        return self.data[key]

    def _set_all_none(self):
        self.data = {key: None for key in self._query_attrs}
