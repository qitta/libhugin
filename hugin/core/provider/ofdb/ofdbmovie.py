#!/usr/bin/env python
# encoding: utf-8

from urllib.parse import quote
import os

from hugin.common.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.genrenorm import GenreNormalize
from hugin.core.provider.ofdb.ofdbcommon import OFDBCommon
import hugin.core.provider as provider


class OFDBMovie(provider.IMovieProvider):
    def __init__(self):
        self._priority = 90
        self._common = OFDBCommon()
        self._genrenorm = GenreNormalize('ofdb.genre')
        self._attrs = {
            'title', 'original_title', 'plot', 'imdbid', 'vote_count',
            'rating', 'directors', 'writers', 'outline', 'year', 'poster',
            'countries', 'genre', 'genre_norm', 'actors'
        }

    def build_url(self, search_params):
        # not enough search params
        if search_params['title'] is None and search_params['imdbid'] is None:
            return None

        # try to search by imdbid if available, else use title
        if search_params['imdbid']:
            path, query = 'imdb2ofdb_json', search_params['imdbid']
        else:
            path, query = 'search_json', quote(search_params['title'])
        return [self._common.base_url.format(path=path, query=query)]

    def parse_response(self, url_response, search_params):
        # validate the response data
        status, retvalue, url, response = self._common.validate_url_response(
            url_response
        )

        if status in ['retry', 'critical']:
            return retvalue

        # validate the response status of the provider
        status, retv = self._common.check_response_status(response)

        if status in ['critical', 'unknown', 'no_data']:
            return retv

        response_type = response['status']['modul']
        response = response['resultat']

        if 'search' in response_type:
            return self._parse_search_module(response, search_params), False

        if 'imdb2ofdb' in response_type:
            return self._parse_imdb2ofdb_module(response, search_params), False

        if 'movie' in response_type:
            return self._parse_movie_module(response, search_params), True

        return None, True

    def _parse_imdb2ofdb_module(self, result, _):
        return self._common.movieids_to_urllist([result['ofdbid']])

    def _parse_search_module(self, result, search_params):
        # create similarity matrix for title, check agains german and original
        # title, higher ratio wins
        similarity_map = []
        for result in result['eintrag']:
            # Get the title with the highest similarity ratio:
            ratio = 0.0
            if 'TV-Mini-Serie' not in result['titel_de'] and 'TV-Serie' not in result['titel_de']:
                for title_key in ['titel_de', 'titel_orig']:
                    ratio = max(
                        ratio,
                        string_similarity_ratio(
                            result[title_key],
                            search_params['title']
                        )
                    )
                similarity_map.append({'ofdbid': result['id'], 'ratio': ratio})

        # sort by ratio, generate ofdbid list with requestet item count
        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])
        matches = [item['ofdbid'] for item in similarity_map[:item_count]]
        return self._common.movieids_to_urllist(matches)

    def _parse_movie_module(self, result, _):
        result_dict = {k: None for k in self._attrs}

        #str attrs
        result_dict['title'] = result['titel']
        result_dict['original_title'] = result['alternativ']
        result_dict['plot'] = result['beschreibung']
        result_dict['outline'] = result['kurzbeschreibung']
        result_dict['imdbid'] = 'tt{0}'.format(result['imdbid'])
        result_dict['rating'] = result['bewertung']['note']

        # number attrs
        result_dict['vote_count'] = int(result['bewertung']['stimmen'])
        result_dict['year'] = int(result['jahr'])

        # list attrs
        result_dict['poster'] = [(None, result['bild'])]
        result_dict['countries'] = result['produktionsland']
        result_dict['actors'] = self._extract_person(result['besetzung'])
        result_dict['directors'] = [r['name'] for r in result['regie']]
        result_dict['writers'] = self._extract_person(result['drehbuch'])
        result_dict['genre'] = result['genre']
        result_dict['genre_norm'] = self._genrenorm.normalize_genre_list(
            result_dict['genre']
        )

        return result_dict

    def _extract_person(self, persons):
        person_list = []
        try:
            for person in persons:
                role, name = person.get('rolle'), person.get('name')
                if role:
                    person_list.append((role, name))
                else:
                    person_list.append(name)
        except (AttributeError, TypeError):
            return []
        return person_list

    @property
    def supported_attrs(self):
        return self._attrs
