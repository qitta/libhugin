#!/usr/bin/env python
# encoding: utf-8


from hugin.common.utils.stringcompare import string_similarity_ratio
from urllib.parse import urlencode
from urllib.parse import quote_plus
import hugin.core.provider as provider
import json


class OMDBMovie(provider.IMovieProvider):

    def __init__(self):
        self._base_url = 'http://www.omdbapi.com/?{query}&plot=full'
        self._attrs = [
            'title', 'year', 'poster', 'imdbid', 'rating', 'actors',
            'director', 'writer', 'genre', 'plot', 'runtime', 'vote_count'
        ]

    def search(self, search_params):
        if search_params['imdbid']:
            params = {
                'i': search_params['imdbid']
            }
        elif search_params['title']:
            params = {
                's': quote_plus(search_params['title']) or '',
                'y': search_params['year'] or ''
            }
        else:
            return None
        return self._base_url.format(query=urlencode(params))

    def parse(self, response, search_params):
        fail_states = ['Incorrect IMDb ID', 'Movie not found!']
        try:
            response = json.loads(response)
        except TypeError:
            return (None, True)
        else:
            if 'Error' in response:
                if response['Error'] in fail_states:
                    return ([], True)
                else:
                    return (None, True)
            if 'Search' in response:
                return self._parse_search_module(response, search_params)

            return self._parse_movie_module(response, search_params)

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['Search']:
            ratio = string_similarity_ratio(
                result['Title'],
                search_params['title']
            )
            similarity_map.append({'imdbid': result['imdbID'], 'ratio': ratio})

        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])
        matches = [item['imdbid'] for item in similarity_map[:item_count]]
        return (self._build_movie_url(matches), False)

    def _build_movie_url(self, matches):
        url_list = []
        for item in matches:
            query = 'i={imdb_id}'.format(imdb_id=item)
            url_list.append(
                self._base_url.format(query=query)
            )
        return url_list

    def _parse_movie_module(self, data, search_params):

        result = {
            'title': data['Title'],
            'year': data['Year'],
            'poster': (None, data['Poster']),
            'imdbid': data['imdbID'],
            'rating': data['imdbRating'],
            'actors': data['Actors'].split(','),
            'director': data['Director'].split(','),
            'writer': data['Writer'].split(','),
            'genre': data['Genre'].split(','),
            'plot': data['Plot'].split(','),
            'runtime': data['Runtime'].split(','),
            'vote_count': data['imdbVotes'].replace(',', '')
        }
        return (result, True)

    @property
    def supported_attrs(self):
        return self._attrs

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
