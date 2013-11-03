#!/usr/bin/env python
# encoding: utf-8


from hugin.common.utils.stringcompare import string_similarity_ratio
import hugin.core.provider as provider
import hugin.core.provider.tmdb as tmdb_common
from urllib.parse import quote
import json


class TMDBPerson(provider.IPersonProvider):
    def __init__(self):
        self._api_key = tmdb_common.get_api_key()
        self._base_url = tmdb_common.get_base_url()
        self._path = 'search/movie'

    def search(self, search_params):
        if search_params['title']:
            title = quote(search_params['title'])
            query = '{title}&year={year}'.format(
                title=title,
                year=search_params['year'] or ''
            )
            return (
                self._base_url.format(
                    path=self._path,
                    apikey=self._api_key,
                    query=query
                ),
                False
            )
        else:
            return (None, True)

    def parse(self, response, search_params):
        tmdb_response = json.loads(response)
        if 'total_results' in tmdb_response:
            if tmdb_response['total_results'] == 0:
                return ([], True)
            else:
                return self._parse_search_module(tmdb_response, search_params)
        elif 'adult' in tmdb_response:
            return self._parse_movie_module(tmdb_response, search_params)
        else:
            return (None, False)

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['results']:
            ratio = 0.0
            for title_key in ['original_title', 'title']:
                ratio = max(
                    ratio,
                    string_similarity_ratio(
                        result[title_key],
                        search_params['title']
                    )
                )
            similarity_map.append({'tmdbid': result['id'], 'ratio': ratio})

        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])
        matches = [item['tmdbid'] for item in similarity_map[:item_count]]
        return (self._build_movie_url(matches), False)

    def _build_movie_url(self, matches):
        url_list = []
        for tmdbid in matches:
            path = 'movie/{tmdbid}'.format(tmdbid=tmdbid)
            url_list.append(
                self._base_url.format(
                    path=path,
                    apikey=self._api_key,
                    query='&language=de'
                )
            )
        return url_list

    def _parse_movie_module(self, data, search_params):
        result = {
            'title': data['title'],
            'year': data['release_date'][:4],
            'imdbid': data['imdb_id'],
        }
        return (result, True)

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
