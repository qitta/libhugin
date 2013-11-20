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
            'providerid', 'homepage', 'deathday', 'popularity', 'biography'
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
        results = {}
        url_response, flag = self._config.validate_response(url_response)
        if flag is True:
            return (None, flag)
        for url, response in url_response:
            if 'search/person?' in url:
                if response['total_results'] == 0:
                    return ([], True)
                else:
                    return self._parse_search_module(response, search_params)
            if '/images?' in url:
                results['images'] = self._parse_images(response)
            elif '/movie_credits?' in url:
                results['movie_credits'] = response
            elif '/person/' in url:
                results['person'] = response
            else:
                return (None, True)
        result = self._concat_result(results)
        return (result, True)

    def _concat_result(self, results):
        data = results['person']
        if 'images' not in results:
            results['images'] = {'posters': [], 'backdrops': []}

        credits = self._extract_movie_credits(results['movie_credits'])
        result = {
            'name': data['name'],
            'photo': results['images'],
            'birthday': data['birthday'],
            'placeofbirth': data['place_of_birth'],
            'imdbid': data['imdb_id'],
            'providerid': data['id'],
            'homepage': data['homepage'],
            'deathday': data['deathday'],
            'popularity': data['popularity'],
            'biography': data['biography'],
            'known_for': credits['cast']
        }
        return result

    def _extract_movie_credits(self, response):
        result = defaultdict(set)
        for person in response['cast']:
            actor = (person['character'], person['original_title'])
            result['cast'].add(actor)
        return result


    def _parse_images(self, response):
        images = []
        for item in response['profiles']:
            images.append(
                    self._config.get_image_url(
                    item['file_path'],
                    'profile'
                )
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
