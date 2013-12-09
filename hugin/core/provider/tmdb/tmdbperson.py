#!/usr/bin/env python
# encoding: utf-8

from urllib.parse import quote

from hugin.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
import hugin.core.provider as provider


class TMDBPerson(provider.IPersonProvider, provider.IPictureProvider):
    def __init__(self):
        self._config = TMDBConfig.get_instance()
        self._priority = 100
        self._attrs = [
            'name', 'photo', 'birthday', 'placeofbirth', 'imdbid',
            'providerid', 'homepage', 'deathday', 'popularity', 'biography',
            'known_for'
        ]

    def build_url(self, search_params):
        if search_params.name:
            return [
                self._config.baseurl.format(
                    path='search/person',
                    apikey=self._config.apikey,
                    query=quote(search_params.name)
                )
            ]

    def parse_response(self, url_response, search_params):
        url, response = self._config.validate_url_response(url_response)

        if response is None or response and 'status_code' in response:
            return None, True

        if 'search/person?' in url and response['total_results'] == 0:
            return [], True

        if 'search/person?' in url:
            return self._parse_search_response(response, search_params), False

        if '/person/' in url:
            return self._build_result_dict(response), True

        return None, True

    def _build_result_dict(self, response):
        result_dict = {k: None for k in self._attrs}
        direct_mapping_str = ['name', 'birthday', 'deathday', 'biography']

        #str attrs
        result_dict['popularity'] = str(response['popularity'])
        result_dict['providerid'] = str(response['id'])
        result_dict['placeofbirth'] = str(response['place_of_birth'])
        result_dict['imdbid'] = response['imdb_id']
        for key in self._attrs:
            if key in direct_mapping_str:
                result_dict[key] = response[key]

        #list attrs
        result_dict['homepage'] = [response['homepage']]

        image_entry = response.get('images')
        if image_entry:
            result_dict['photo'] = self._config.extract_image_by_type(response, 'profiles')

        result_dict['known_for'] = self._parse_movie_credits(
            response['movie_credits']
        )
        return result_dict

    def _parse_search_response(self, response, search_params):
        similarity_map = []
        for item in response['results']:
            ratio = string_similarity_ratio(
                item['name'],
                search_params.name
            )
            similarity_map.append({'tmdbid': item['id'], 'ratio': ratio})

        similarity_map.sort(key=lambda value: value['ratio'], reverse=True)
        item_count = min(len(similarity_map), search_params.amount)
        movie_ids = [item['tmdbid'] for item in similarity_map[:item_count]]
        return self._config.build_person_urllist(movie_ids, search_params)

    def _parse_movie_credits(self, response):
        credits = []
        for person in response['cast']:
            character_movie = (person['character'], person['original_title'])
            credits.append(character_movie)
        return credits

    @property
    def supported_attrs(self):
        return self._attrs
