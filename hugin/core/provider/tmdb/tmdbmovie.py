#!/usr/bin/env python
# encoding: utf-8


from hugin.common.utils.stringcompare import string_similarity_ratio
import hugin.core.provider as provider
from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
from urllib.parse import quote_plus
import json


class TMDBMovie(provider.IMovieProvider):
    def __init__(self):
        self._config = TMDBConfig()
        self._path = 'search/movie'
        self._attrs = ['title', 'original_title', 'imdbid', 'genre', 'plot']

    def search(self, search_params):
        if search_params['imdbid']:
            return ''.join(self._build_movie_url([search_params['imdbid']]))

        if search_params['title']:
            title = quote_plus(search_params['title'])
            query = '{title}&year={year}'.format(
                title=title,
                year=search_params['year'] or ''
            )
            return self._config.baseurl.format(
                path=self._path,
                apikey=self._config.apikey,
                query=query
            )
        else:
            return None

    def parse(self, response, search_params):
        try:
            tmdb_response = json.loads(response)
        except TypeError as e:
            return (None, True)
        if 'total_results' in tmdb_response:
            if tmdb_response['total_results'] == 0:
                return ([], True)
            else:
                return self._parse_search_module(tmdb_response, search_params)
        elif 'adult' in tmdb_response:
            return self._parse_movie_module(tmdb_response, search_params)
        elif 'status_code' in tmdb_response:
            return (None, True)

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['results']:
            if result is not None:
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
                self._config.baseurl.format(
                    path=path,
                    apikey=self._config.apikey,
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

    @property
    def supported_attrs(self):
        return self._attrs

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
