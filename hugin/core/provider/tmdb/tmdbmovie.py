#!/usr/bin/env python
# encoding: utf-8


from urllib.parse import quote_plus
from collections import defaultdict
import os

from hugin.core.provider.tmdb.tmdbcommon import TMDBConfig
from hugin.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.genrenorm import GenreNormalize
import hugin.core.provider as provider


class TMDBMovie(provider.IMovieProvider, provider.IMoviePictureProvider):
    def __init__(self):
        self._config = TMDBConfig.get_instance()
        self._priority = 100
        self._genrenorm = GenreNormalize('tmdb.genre')
        self._attrs = {
            'title', 'original_title', 'plot', 'runtime', 'imdbid',
            'vote_count', 'rating', 'providerid', 'alternative_titles',
            'directors', 'writers', 'crew', 'year', 'poster', 'fanart',
            'countries', 'genre', 'genre_norm', 'collection', 'studios',
            'trailers', 'actors', 'keywords', 'tagline'
        }

    def build_url(self, search_params):
        if search_params.imdbid:
            return self._config.build_movie_urllist(
                [search_params.imdbid],
                search_params
            ).pop()

        if search_params.title:
            title = quote_plus(search_params.title)
            query = '{title}&year={year}&language={language}'.format(
                title=title,
                year=search_params.year or '',
                language=search_params.language or ''
            )
            return [self._config.baseurl.format(
                path='search/movie',
                apikey=self._config.apikey,
                query=query
            )]

    def parse_response(self, url_response, search_params):
        url, response = self._config.validate_url_response(url_response)

        if response is None or response and 'status_code' in response:
            return None, True

        if 'search/movie?' in url and response['total_results'] == 0:
            return [], True

        if 'search/movie?' in url:
            return self._parse_search_module(response, search_params), False

        if '/movie/' in url:
            return self._parse_movie_module(response), True

        return None, True

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
                            search_params.title
                        )
                    )
                similarity_map.append({'tmdbid': result['id'], 'ratio': ratio})

        similarity_map.sort(key=lambda value: value['ratio'], reverse=True)
        item_count = min(len(similarity_map), search_params.amount)
        movieids = [item['tmdbid'] for item in similarity_map[:item_count]]
        return self._config.build_movie_urllist(movieids, search_params)

    def _parse_movie_module(self, result):
        result_dict = {key: None for key in self._attrs}

        # str attrs
        strattr_keymap = [
            'imdbid:imdb_id', 'plot:overview', 'rating:vote_average',
            'title:title', 'original_title:original_title', 'providerid:id',
            'tagline:tagline'
        ]
        for keymap in strattr_keymap:
            key_result, key_response = keymap.split(':', maxsplit=1)
            result_dict[key_result] = str(result[key_response])

        # list attrs
        crew = self._config.extract_keyvalue_attrs(
            result['credits']['crew'], key_a='job', key_b='name'
        )
        result_dict['directors'] = [n for j, n in crew if j == 'Director']
        result_dict['writers'] = [n for j, n in crew if j == 'Writer']
        result_dict['crew'] = [(j, n) for j, n in crew if j not in ['Director', 'Writer']]
        result_dict['actors'] = self._config.extract_keyvalue_attrs(
            result['credits']['cast'], key_a='character', key_b='name'
        )
        result_dict['poster'] = self._config.extract_image_by_type(
            result, 'posters'
        )
        result_dict['fanart'] = self._config.extract_image_by_type(
            result, 'backdrops'
        )
        result_dict['trailers'] = self._extract_trailers(result['trailers'])
        result_dict['collection'] = [result['belongs_to_collection']]
        result_dict['alternative_titles'] = self._config.extract_keyvalue_attrs(
            result['alternative_titles']['titles'], 'iso_3166_1', 'title'
        )
        listattr_keymap = [
            'studios:production_companies', 'genre:genres',
            'countries:production_countries'
        ]
        for keymap in listattr_keymap:
            key_result, key_response = keymap.split(':', maxsplit=1)
            result_dict[key_result] = self._config.extract_keyvalue_attrs(
                result[key_response], 'name'
            )
        result_dict['genre_norm'] = self._genrenorm.normalize_genre_list(
            result_dict['genre']
        )
        result_dict['keywords'] = self._config.extract_keyvalue_attrs(
            result['keywords']['keywords'], 'name'
        )

        # numeric attrs
        result_dict['year'] = int(result['release_date'][0:4] or 0) or None
        result_dict['runtime'] = int(result['runtime'] or 0) or None
        result_dict['vote_count'] = int(result['vote_count'] or 0) or None
        return result_dict

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

    @property
    def supported_attrs(self):
        return self._attrs
