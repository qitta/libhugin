#!/usr/bin/env python
# encoding: utf-8


from hugin.common.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.genrenorm import GenreNormalize
from urllib.parse import urlencode
from urllib.parse import quote_plus
from parse import parse
import hugin.core.provider as provider
import json
import os


class OMDBMovie(provider.IMovieProvider):

    def __init__(self):
        self._base_url = 'http://www.omdbapi.com/?{query}&plot=full'
        self._genrenorm = GenreNormalize(
            os.path.abspath('hugin/core/provider/omdb.genre')
        )
        self._priority = 80
        self._attrs = {
            'title': 'Title',
#            'original_title': None,
            'plot': '__Plot',
            'runtime': '__Runtime',
            'imdbid': 'imdbID',
            'vote_count': '__imdbVotes',
            'rating': 'imdbRating',
#            'providerid': None,
#            'alternative_titles': None,
            'directors': '__Director',
            'writers': '__Writer',
#            'crew': None,
            'year': 'Year',
            'poster': '__Poster',
#            'fanart': None,
#            'countries': None,
            'genre': '__Genre',
            'genre_norm': '__genre_norm',
#            'collection': None,
#            'studios': None,
#            'trailers': None,
            'actors': '__Actors',
#            'keywords': None,
#            'tagline': None,
#            'outline' : None
        }

    def build_url(self, search_params):
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
        return [self._base_url.format(query=urlencode(params))]

    def parse_response(self, url_response, search_params):
        fail_states = ['Incorrect IMDb ID', 'Movie not found!']
        first_element, *_ = url_response
        _, response = first_element
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
            if result['Type'] == 'movie':
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
            url = self._base_url.format(query=query)
            url_list.append([url])
        return url_list

    def _parse_movie_module(self, data, search_params):

        result_map = {}
        result_map['Poster'] = list((None, data['Poster']))
        result_map['Actors'] = data['Actors'].split(',')
        result_map['Director'] = data['Director'].split(',')
        result_map['Writer'] = data['Writer'].split(',')
        result_map['Genre'] = data['Genre'].split(',')
        result_map['Plot'] = ''.join(data['Plot'].split(',')) or ''
        result_map['imdbVotes'] = int(data['imdbVotes'].replace(',', ''))
        result_map['Runtime'] = self._format_runtime(data['Runtime'])
        result_map['genre_norm'] = self._genrenorm.normalize_genre_list(
            result_map['Genre']
        )
        data['Year'] = int(data['Year'])

        result_dict = {key: None for key in self._attrs}
        for key, value in self._attrs.items():
            if value is not None:
                if value.startswith('__'):
                    result_dict[key] = self._filter_na(result_map[value[2:]])
                else:
                    result_dict[key] = self._filter_na(data[value])

        return (result_dict, True)

    def _filter_na(self, result):
        if result == 'N/A':
            return ''
        elif result == ['N/A']:
            return []
        else:
            return result

    def _format_runtime(self, runtime):
        result = []
        if runtime and 'h' in runtime and 'min' in runtime:
            h, m = parse('{:d} h {:d} min', runtime)
            result = (h * 60) + m
        elif 'min' in runtime:
            result, = parse('{:d} min', runtime)
        elif 'h' in runtime:
            result, = parse('{:d} h', runtime)
        return int(result)

    @property
    def supported_attrs(self):
        return [k for k, v in self._attrs.keys() if v is not None]

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
