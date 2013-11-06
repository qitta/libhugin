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
            return self._config.baseurl.format(
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
        return (self._config.build_movie_url(matches, search_params), False)

    def _parse_movie_module(self, data, search_params):
        result = {
            'name': data['name'],
            'photo': self._config.get_image_url(
                data['profile_path'],
                'profile'
            ),
            'birthday': data['birthday'],
            'placeofbirth': data['place_of_birth'],
            'imdbid': data['imdb_id'],
            'providerid': data['id'],
            'homepage': data['homepage'],
            'deathday': data['deathday'],
            'popularity': data['popularity'],
            'biography': data['biography']
        }
        return (result, True)

    def activate(self):
        provider.IMovieProvider.activate(self)
        self._config = TMDBConfig.get_instance()
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
