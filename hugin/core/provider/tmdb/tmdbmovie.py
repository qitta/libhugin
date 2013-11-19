#!/usr/bin/env python
# encoding: utf-8


from urllib.parse import quote_plus

from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
from hugin.utils import get_movie_result_dict
from hugin.common.utils.stringcompare import string_similarity_ratio
import hugin.core.provider as provider


class TMDBMovie(provider.IMovieProvider, provider.IPictureProvider):
    def __init__(self):
        self._config = TMDBConfig.get_instance()
        self._path = 'search/movie'
        self._attrs = ['title', 'original_title', 'plot', 'year', 'imdbid',
            'poster', 'fanart', 'vote_count', 'rating', 'countries', 'genre',
            'providerid', 'collection', 'runtime', 'studios'
        ]

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
        results = {}
        url_response, flag = self._config.validate_response(url_response)
        if flag is True:
            return (None, flag) # what if just one url fails?
        for url, response in url_response:
            if 'search/movie?' in url:
                if response['total_results'] == 0:
                    return ([], True)
                else:
                    return self._parse_search_module(response, search_params)
            if '/images?' in url:
                results['images'] = self._parse_images(response)
            elif '/casts?' in url:
                results['casts'] = response
            elif '/movie/' in url:
                results['movie'] = response
            else:
                return (None, True)

        result = self._concat_result(results)
        return (result, True)

    def _parse_images(self, response):
        result = {'posters': [], 'backdrops': []}
        for item in response['posters']:
            result['posters'].append(
                    self._config.get_image_url(
                    item['file_path'],
                    'poster'
                )
            )
        for item in response['backdrops']:
            result['backdrops'].append(
                    self._config.get_image_url(
                    item['file_path'],
                    'backdrop'
                )
            )
        return result

    def _concat_result(self, results):
        data = results['movie']
        if 'images' not in results:
            results['images'] = {'posters': [], 'backdrops': []}

        result = {
            'title': data['title'],
            'original_title': data['title'],
            'plot': data['overview'],
            'year': data['release_date'][:4],
            'imdbid': data['imdb_id'],
            'poster': results['images']['posters'],
            'fanart': results['images']['backdrops'],
            'vote_count': data['vote_count'],
            'rating': data['vote_average'],
            'countries': self._config.extract_keyvalue_attrs(
                data['production_countries']
            ),
            'genre': self._config.extract_keyvalue_attrs(
                data['genres']
            ),
            'providerid': data['id'],
            'collection': data['belongs_to_collection'],
            'runtime': data['runtime'],
            'studios': self._config.extract_keyvalue_attrs(
                data['production_companies']
            )
        }
        return result

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

    def _parse_movie_module(self, data, search_params):
        """
        .. TODO please use the result dict
        """
        result = {
            'title': data['title'],
            'original_title': data['title'],
            'plot': data['overview'],
            'year': data['release_date'][:4],
            'imdbid': data['imdb_id'],
            'poster': self._config.get_image_url(
                data['poster_path'],
                'poster'
            ),
            'fanart': self._config.get_image_url(
                data['backdrop_path'],
                'backdrop'
            ),
            'vote_count': data['vote_count'],
            'rating': data['vote_average'],
            'countries': self._config.extract_keyvalue_attrs(
                data['production_countries']
            ),
            'genre': self._config.extract_keyvalue_attrs(
                data['genres']
            ),
            'providerid': data['id'],
            'collection': data['belongs_to_collection'],
            'runtime': data['runtime'],
            'studios': self._config.extract_keyvalue_attrs(
                data['production_companies']
            )
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
