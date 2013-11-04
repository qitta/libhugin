#!/usr/bin/env python
# encoding: utf-8


from hugin.common.utils.stringcompare import string_similarity_ratio
import hugin.core.provider as provider
from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
from urllib.parse import quote
import json


class TMDBPerson(provider.IPersonProvider):
    def __init__(self):
        self._config = TMDBConfig()
        self._path = 'search/person'

    def search(self, search_params):
        if search_params['name']:
            name = quote(search_params['name'])
            query = '{name}'.format(
                name=name
            )
            return  self._config.baseurl.format(
                path=self._path,
                apikey=self._config.apikey,
                query=query
            )
        else:
            return None

    def parse(self, response, search_params):
        tmdb_response = json.loads(response)
        if 'total_results' in tmdb_response:
            if tmdb_response['total_results'] == 0:
                return ([], True)
            else:
                return self._parse_search_module(tmdb_response, search_params)
        elif 'name' in tmdb_response:
            return self._parse_movie_module(tmdb_response, search_params)
        else:
            return (None, False)

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['results']:
            ratio = 0.0
            for title_key in ['name']:
                ratio = max(
                    ratio,
                    string_similarity_ratio(
                        result[title_key],
                        search_params['name']
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
            path = 'person/{tmdbid}'.format(tmdbid=tmdbid)
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
            'name': data['name'],
            'photo': self._get_image_url(data['profile_path']),
            'imdbid': data['imdb_id'],
            'birthday': data['birthday'],
            'deathday': data['deathday'],
            'biography': data['biography']
        }
        return (result, True)

    def _get_image_url(self, profile_path):
        return 'http://d3gtl9l2a4fn1j.cloudfront.net/t/p/w185/{0}'.format(profile_path)

    def activate(self):
        provider.IMovieProvider.activate(self)
        self._config = TMDBConfig.get_instance()
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
