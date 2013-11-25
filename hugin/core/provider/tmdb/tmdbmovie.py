#!/usr/bin/env python
# encoding: utf-8


'''

.. py:function:: attribute_format

    :param title: Was ist der title
    :type title: [str]

'''

from urllib.parse import quote_plus
import os

from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
from hugin.common.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.genrenorm import GenreNormalize
from collections import defaultdict
import hugin.core.provider as provider


class TMDBMovie(provider.IMovieProvider, provider.IPictureProvider):
    def __init__(self):
        self._config = TMDBConfig.get_instance()
        self._priority = 100
        self._path = 'search/movie'
        self._genrenorm = GenreNormalize(
            os.path.abspath('hugin/core/provider/tmdb.genre')
        )
        self._attrs = {
            'title': 'title',
            'original_title': 'original_title',
            'plot': 'overview',
            'runtime': 'runtime',
            'imdbid': 'imdb_id',
            'vote_count': 'vote_count',
            'rating': 'vote_average',
            'providerid': 'id',
            'alternative_titles': '__alternative_titles',
            'directors': '__directors',
            'writers': '__writers',
            'crew': '__crew',
            'year': '__year',
            'poster': '__posters',
            'fanart': '__backdrops',
            'countries': '__production_countries',
            'genre': '__genres',
            'genre_norm': '__genre_norm',
            'collection': '__belongs_to_collection',
            'studios': '__production_companies',
            'trailers': '__trailers',
            'actors': '__actors',
            'keywords': '__keywords',
            'tagline': 'tagline',
            'outline': None
        }

    def build_url(self, search_params):
        if search_params['imdbid']:
            return self._config.build_movie_url(
                [search_params['imdbid']],
                search_params
            ).pop()

        if search_params['title']:
            title = quote_plus(search_params['title'])
            query = '{title}&year={year}&language={language}'.format(
                title=title,
                year=search_params['year'] or '',
                language=search_params['language'] or ''
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

        if 'search/movie?' in url:
            if response['total_results'] == 0:
                return ([], True)
            else:
                return self._parse_search_module(response, search_params)
        else:
            return (self._concat_result(response), True)

    def _concat_result(self, results):
        if 'images' not in results:
            results['images'] = {'posters': [], 'backdrops': []}

        result_map = {}
        result_map['year'] = results['release_date'][0:4]

        directors, writers, actors, crew = self._extract_credits(
            results['credits']
        )
        result_map['directors'] = directors
        result_map['writers'] = writers
        result_map['actors'] = actors
        result_map['crew'] = crew

        result_map['keywords'] = self._config.extract_keyvalue_attrs(
            results['keywords']['keywords']
        )
        posters, backdrops = self._extract_images(results['images'])
        result_map['posters'] = posters
        result_map['backdrops'] = backdrops

        result_map['belongs_to_collection'] = results['belongs_to_collection']
        result_map['alternative_titles'] = self._extract_alternative_titles(
            results['alternative_titles']
        )
        result_map['trailers'] = self._extract_trailers(results['trailers'])
        for item in ['genres', 'production_companies', 'production_countries']:
            result_map[item] = self._config.extract_keyvalue_attrs(
                results[item]
            )
        result_map['genre_norm'] = self._genrenorm.normalize_genre_list(
            result_map['genres']
        )

        # filling the result dictionary
        result_dict = {}
        for key, value in self._attrs.items():
            if value is not None:
                if value.startswith('__'):
                    result_dict[key] = result_map[value[2:]] or []
                else:
                    result_dict[key] = results[value] or []
        return result_dict

    def _extract_images(self, response):
        posters = []
        backdrops = []

        for item in response['posters']:
            posters += self._config.get_image_url(
                item['file_path'],
                'poster'
            )
        for item in response['backdrops']:
            backdrops.append(
                self._config.get_image_url(
                    item['file_path'],
                    'backdrop'
                )
            )
        return posters,  backdrops

    def _extract_trailers(self, response):
        yt_url = 'http://www.youtube.com/watch\\?v\\={path}'
        result = []
        for path in response['youtube']:
            trailer_url = (path['size'], yt_url.format(path=path['source']))
            result.append(trailer_url)
        for source in response['quicktime']:
            for path in source['sources']:
                trailer_url = (path['size'], path['source'])
                result.append(trailer_url)
        return result

    def _extract_alternative_titles(self, response):
        titles = []
        for title in response['titles']:
            title = (title['iso_3166_1'], title['title'])
            titles.append(title)
        return titles

    def _extract_credits(self, credits):
        result = defaultdict(set)
        for person in credits['cast']:
            actor = (person['character'], person['name'])
            result['cast'].add(actor)
        for person in credits['crew']:
            result[person['department']].add(person['name'])

        directors = result.pop('Directing', [])
        writers = result.pop('Writing', [])
        casts = result.pop('cast', [])
        crew = result['crew'] or []
        return directors, writers, casts, crew

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
        return (self._config.build_movie_url(matches, search_params), False)

    @property
    def supported_attrs(self):
        return [k for k, v in self._attrs.items() if v is not None]

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
