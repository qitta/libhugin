#!/usr/bin/env python
# encoding: utf-8

# stdlib
from parse import parse
from urllib.parse import urlencode, quote_plus
import json
import os

#hugin
from hugin.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.genrenorm import GenreNormalize
import hugin.core.provider as provider


class OMDBMovie(provider.IMovieProvider):
    """ OMDB Person text metadata provider.

    Interfaces implemented according to hugin.provider.interfaces.

    """

    def __init__(self):
        self._base_url = 'http://www.omdbapi.com/?{query}&plot=full'
        self._genrenorm = GenreNormalize('omdb.genre')
        self._priority = 80
        self._attrs = {
            'title', 'plot', 'runtime', 'imdbid', 'vote_count', 'rating',
            'directors', 'writers', 'year', 'poster', 'genre', 'genre_norm',
            'actors', 'original_title'
        }

    def build_url(self, search_params):
        if search_params.imdbid:
            params = {
                'i': search_params.imdbid
            }
            return [self._base_url.format(query=urlencode(params))]
        if search_params.title:
            params = {
                's': quote_plus(search_params.title) or '',
                'y': search_params.year or ''
            }
            return [self._base_url.format(query=urlencode(params))]

    def parse_response(self, url_response, search_params):
        fail_states = ['Incorrect IMDb ID', 'Movie not found!']

        try:
            url, response = url_response.pop()
            response = json.loads(response)
        except (TypeError, ValueError):
            return None, True

        if 'Error' in response and response['Error'] in fail_states:
            return [], True

        if 'Search' in response:
            return self._parse_search_module(response, search_params), False

        if 'Title' in response:
            return self._parse_movie_module(response, search_params), True

        return None, True

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['Search']:
            if result['Type'] == 'movie':
                ratio = string_similarity_ratio(
                    result['Title'],
                    search_params.title
                )
                similarity_map.append(
                    {'imdbid': result['imdbID'], 'ratio': ratio}
                )
        similarity_map.sort(key=lambda value: value['ratio'], reverse=True)
        item_count = min(len(similarity_map), search_params.amount)
        movieids = [item['imdbid'] for item in similarity_map[:item_count]]
        return self._movieids_to_urllist(movieids)

    def _movieids_to_urllist(self, movieids):
        url_list = []
        for movieid in movieids:
            query = 'i={imdb_id}'.format(imdb_id=movieid)
            url_list.append([self._base_url.format(query=query)])
        return url_list

    def _parse_movie_module(self, result, search_params):
        result_dict = {k: None for k in self._attrs}

        #str attrs
        result_dict['title'] = ''.join(result['Title'].split(','))
        result_dict['original_title'] = result_dict['title']
        result_dict['plot'] = ''.join(result['Plot'].split(','))
        result_dict['imdbid'] = result['imdbID']
        result_dict['rating'] = result['imdbRating']

        #list attrs
        result_dict['poster'] = [(None, result['Poster'])]
        result_dict['actors'] = result['Actors'].split(',')
        result_dict['actors'] = [(None, a) for a in result_dict['actors']]
        result_dict['directors'] = result['Director'].split(',')
        result_dict['writers'] = result['Writer'].split(',')
        result_dict['genre'] = result['Genre'].split(',')
        result_dict['genre_norm'] = self._genrenorm.normalize_genre_list(
            result_dict['genre']
        )

        #numeric attrs
        result_dict['runtime'] = int(self._format_runtime(result['Runtime']))
        vote_count = result['imdbVotes'].replace(',', '')
        if vote_count.isnumeric():
            result_dict['vote_count'] = int(vote_count)
        result_dict['year'] = int(result['Year'])

        return {key: self._filter_na(val) for key, val in result_dict.items()}

    def _filter_na(self, value):
        if value == 'N/A':
            return ''
        if value == ['N/A']:
            return []
        return value

    def _format_runtime(self, runtime):
        result = 0
        time_fmt = {'HM': '{:d} h {:d} min', 'H': '{:d} h', 'M': '{:d} min'}
        if runtime and 'h' in runtime and 'min' in runtime:
            h, m = parse(time_fmt['HM'], runtime)
            result = (h * 60) + m
        elif 'min' in runtime:
            result, = parse(time_fmt['M'], runtime)
        elif 'h' in runtime:
            result, = parse(time_fmt['H'], runtime)
        return result

    @property
    def supported_attrs(self):
        return self._attrs
