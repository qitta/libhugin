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
        self._attrs = {
            'name': 'name',
            'alternative_name': None,
            'photo': '__images',
            'birthday': 'birthday',
            'placeofbirth': 'place_of_birth',
            'imdbid': 'imdb_id',
            'providerid': 'id',
            'homepage': 'homepage',
            'deathday': 'deathday',
            'popularity': 'popularity',
            'biography': 'biography',
            'known_for': '__cast'
        }
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
        result_map = {}
        if 'images' not in results:
            result_map['images'] = []
        else:
            result_map['images'] = self._parse_images(results['images'])
        result_map['photo'] = result_map['images']
        result_map['known_for'] = result_map['cast'] = self._extract_movie_credits(
            results['movie_credits']
        )

        result_dict = {}
        for key, value in self._attrs.items():
            if value is not None:
                if value.startswith('__'):
                    result_dict[key] = result_map[value[2:]] or []
                else:
                    result_dict[key] = results[value] or []
        return result_dict

    def _extract_movie_credits(self, response):
        result = defaultdict(set)
        for person in response['cast']:
            actor = (person['character'], person['original_title'])
            result['cast'].add(actor)
        return result['cast']

    def _parse_images(self, response):
        images = []
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

    def _parse_person_module(self, data, search_params):
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
        return ([result], True)

    @property
    def supported_attrs(self):
        return self._attrs

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
