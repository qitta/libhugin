#!/usr/bin/env python
# encoding: utf-8


'''

.. py:function:: attribute_format

    :param title: Was ist der title
    :type title: [str]

'''

from urllib.parse import quote_plus

from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
from hugin.common.utils.stringcompare import string_similarity_ratio
from collections import defaultdict
import hugin.core.provider as provider


class TMDBMovie(provider.IMovieProvider, provider.IPictureProvider):
    def __init__(self):
        self._config = TMDBConfig.get_instance()
        self._priority = 100
        self._path = 'search/movie'
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
            'collection': '__belongs_to_collection',
            'studios': '__production_companies',
            'trailers': '__trailers',
            'actors': '__actors',
            'keywords': '__keywords'
        }

    def build_url(self, search_params):
        if search_params['imdbid']:
            return self._config.build_movie_search_url(
                [search_params['imdbid']],
                search_params
            )

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
        url_response, flag = self._config.validate_response(url_response)
        if flag is True:
            return (None, flag)  # what if just one url fails?

        results = {}
        for url, response in url_response:
            if 'search/movie?' in url:
                if response['total_results'] == 0:
                    return ([], True)
                else:
                    return self._parse_search_module(response, search_params)

            key = self._get_key_for_url(url)
            if key is not None:
                results[key] = response
            else:
                return (None, True)

        return (self._concat_result(results), True)

    def _get_key_for_url(self, url):
        for part in [
            '/images?', '/credits?', '/alternative_titles?', '/trailers?',
            '/keywords?', '3/movie/'
        ]:
            if part in url:
                if part == '3/movie/':
                    return part[2:-1]
                else:
                    return part[1:-1]

    def _concat_result(self, results):
        if 'images' not in results:
            results['images'] = {'posters': [], 'backdrops': []}

        result_map = {}
        result_map.setdefault('year', results['movie']['release_date'][0:4])

        directors, writers, actors, crew = self._extract_credits(results['credits'])
        result_map.setdefault('directors', directors)
        result_map.setdefault('writers', writers)
        result_map.setdefault('actors', actors)
        result_map.setdefault('crew', crew)

        result_map.setdefault('keywords', self._config.extract_keyvalue_attrs(
            results['keywords']['keywords'])
        )
        posters, backdrops = self._extract_images(results['images'])
        result_map.setdefault('posters', posters)
        result_map.setdefault('backdrops', backdrops)

        result_map.setdefault(
            'belongs_to_collection',
            results['movie']['belongs_to_collection'] or []
        )
        result_map.setdefault('alternative_titles',
            self._extract_alternative_titles(
                results['alternative_titles']
            )
        )
        result_map.setdefault(
            'trailers', self._extract_trailers(results['trailers'])
        )
        for item in ['genres', 'production_companies', 'production_countries']:
            result_map.setdefault(
                item,
                self._config.extract_keyvalue_attrs(results['movie'][item])
            )

        # filling the result dictionary
        result_dict = {}
        for key, value in self._attrs.items():
            if value.startswith('__'):
                result_dict.setdefault(key, result_map[value[2:]])
            else:
                result_dict.setdefault(key, results['movie'][value] or [])
        return result_dict

    def _extract_images(self, response):
        posters = []
        backdrops = []

        for item in response['posters']:
            posters.append(
                self._config.get_image_url(
                    item['file_path'],
                    'poster'
                )
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
        return self._attrs.keys()

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
