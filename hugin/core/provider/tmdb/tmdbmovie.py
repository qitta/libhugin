#!/usr/bin/env python
# encoding: utf-8


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
            elif '/credits?' in url:
                results['credits'] = response
            elif '/alternative_titles?' in url:
                results['alternative_titles'] = response
            elif '/trailers?' in url:
                results['trailers'] = response
            elif '/keywords?' in url:
                results['keywords'] = response
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

        credits = self._extract_credits(results['credits'])

        alt_titles = self._extract_alternative_titles(results['alternative_titles'])
        trailers = self._extract_trailers(results['trailers'])
        result = {
            'title': data['title'],
            'original_title': data['title'],
            'plot': data['overview'],
            'directors': credits.pop('Directing', []), # [director, ]
            'writer': credits.pop('Writing', []),
            'crew' : credits,
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
            'collection': not data['belongs_to_collection'] or data['belongs_to_collection']['name'],
            'runtime': data['runtime'],
            'studios': self._config.extract_keyvalue_attrs(
                data['production_companies']
            ),
            'trailers': trailers, # (HQ, SQ, None, trailer)
            'actors': credits.pop('cast', []),
            'keywords': self._config.extract_keyvalue_attrs(
                results['keywords']['keywords']
            ),
            'similar_movies': [], # [keywords,]
            'alternative_titles': alt_titles
        }
        return result

    def _extract_trailers(self, response):
        print(response)
        yt_url = 'http://www.youtube.com/watch\\?v\\={path}'
        result = []
        for path in response['youtube']:
            trailer_url = yt_url.format(path=path['source'])
            result.append(trailer_url)
        for source in response['quicktime']:
            for path in source['sources']:
                trailer_url = path['source']
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

    @property
    def supported_attrs(self):
        return self._attrs

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
