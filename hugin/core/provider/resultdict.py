#!/usr/bin/env python
# encoding: utf-8


from collections import UserDict, Iterable


class ResultDict(UserDict):

    def __init__(self, provider_type):
        self.data = {}
        self._movie_attrs = {
            'title': str, 'original_title': Iterable, 'plot': str,
            'runtime': int, 'imdbid': str, 'vote_count': int, 'rating': str,
            'providerid': str, 'alternative_titles': Iterable,
            'directors': Iterable, 'writers': Iterable, 'crew': Iterable,
            'year': int, 'poster': Iterable, 'fanart': Iterable,
            'countries': Iterable, 'genre': Iterable, 'genre_norm': Iterable,
            'collection': Iterable, 'studios': Iterable, 'trailers': Iterable,
            'actors': Iterable, 'keywords': Iterable, 'tagline': str,
            'outline': str
        }
        self._person_attrs = {
            'name': str, 'alternative_names': Iterable, 'photo': Iterable,
            'birthday': str, 'placeofbirth': str, 'imdbid': str,
            'providerid': str, 'homepage': Iterable, 'deathday': str,
            'popularity': str, 'biography': str, 'known_for': Iterable
        }
        self._attrs = {
            'movie': self._movie_attrs, 'person': self._person_attrs
        }.get(provider_type)

    def __setitem__(self, key, value):
        if key in self._attrs:
            if isinstance(value, self._attrs[key]):
                self.data[key] = value
            else:
                self.data[key] = None
        else:
            print('invalid value type {0}.'.format())
