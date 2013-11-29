#!/usr/bin/env python
# encoding: utf-8


from hugin.common.utils.stringcompare import string_similarity_ratio
import hugin.core.provider as provider
from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
from collections import defaultdict
from urllib.parse import quote


class TMDBPerson(provider.IPersonProvider, provider.IPictureProvider):
    def __init__(self):
        self._config = TMDBConfig.get_instance()
        self._priority = 100
        self._attrs = [
            'name', 'photo', 'birthday', 'placeofbirth', 'imdbid',
            'providerid', 'homepage', 'deathday', 'popularity', 'biography',
            'known_for'
        ]
        self._path = 'search/person'

    def build_url(self, search_params):
        if search_params['name']:
            name = quote(search_params['name'])
            query = '{name}'.format(
                name=name
            )
            return [self._config.baseurl.format(
                path=self._path,
                apikey=self._config.apikey,
                query=query
            )]
        else:
            return None

    def parse_response(self, url_response, search_params):
        fr, *_ = url_response
        url, response = fr
        response = self._config.validate_url_response(response)
        if response is None:
            return (None, True)
        elif 'status_code' in response:
            return (None, True)

        if 'search/person?' in url:
            if response['total_results'] == 0:
                return ([], True)
            else:
                return self._parse_search_module(response, search_params)
        else:
            return (self._concat_result(response), True)

    def _concat_result(self, results):
        result_dict = {k: None for k in self._attrs}
        direct_mapping_str = [
            'name', 'birthday', 'deathday', 'biography'
        ]

        #str attrs
        result_dict['popularity'] = str(results['popularity'])
        result_dict['providerid'] = str(results['id'])
        result_dict['placeofbirth'] = str(results['place_of_birth'])
        result_dict['imdbid'] = results['imdb_id']
        for key in self._attrs:
            if key in direct_mapping_str:
                result_dict[key] = results[key]

        #list attrs
        result_dict['homepage'] = list(results['homepage'])
        result_dict['photo'] = self._parse_images(results.get('images'))
        result_dict['known_for'] = self._extract_movie_credits(
            results['movie_credits']
        )
        return result_dict

    def _extract_movie_credits(self, response):
        result = defaultdict(list)
        for person in response['cast']:
            actor = (person['character'], person['original_title'])
            result['cast'].append(actor)
        return result['cast']

    def _parse_images(self, response):
        images = []
        if response:
            for item in response['profiles']:
                images += self._config.get_image_url(
                    item['file_path'], 'profile'
                )
            return images

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
        return (self._config.build_person_url(matches, search_params), False)

    @property
    def supported_attrs(self):
        return self._attrs

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
