#!/usr/bin/env python
# encoding: utf-8

from hugin.common.utils.stringcompare import string_similarity_ratio
import hugin.core.provider as provider
from urllib.parse import quote
import json


class OFDBMovie(provider.IMovieProvider):
    def __init__(self):
        self._base_url = 'http://ofdbgw.home-of-root.de/{path}/{query}'
        self._attrs = ['title', 'year', 'imdbid', 'genre', 'plot']

    def search(self, search_params):
        # not enough search params
        if search_params['title'] is None and search_params['imdbid'] is None:
            return None

        # try to search by imdbid if available, else use title
        if search_params['imdbid']:
            path, query = 'imdb2ofdb_json', search_params['imdbid']
        else:
            path, query = 'search_json', quote(search_params['title'])
        return self._base_url.format(path=path, query=query)

    def parse(self, response, search_params):
        '''
        0 = Keine Fehler
        1 = Unbekannter Fehler
        2 = Fehler oder Timeout bei Anfrage an IMDB bzw. OFDB
        3 = Keine oder falsche ID angebene
        4 = Keine Daten zu angegebener ID oder Query gefunden
        5 = Fehler bei der Datenverarbeitung
        9 = Wartungsmodus, OFDBGW derzeit nicht verfügbar.
        '''
        try:
            ofdb_response = json.loads(response).get('ofdbgw')
        except (TypeError, ValueError):
            ofdb_response = self._try_sanitize(response)
            if ofdb_response is None:
                return (None, True)

        status = ofdb_response['status']

        if status['rcode'] in [4, 9]:
            return ([], True)

        # we want retries to start
        if status['rcode'] in [1, 2, 5]:
            return (None, False)

        if status['rcode'] in [3]:
            return (None, True)

        if status['rcode'] == 0:
            select_parse_method = {
                'movie': self._parse_movie_module,
                'imdb2ofdb': self._parse_imdb2ofdb_module,
                'search': self._parse_search_module
            }.get(status['modul'])

            if select_parse_method is not None:
                return select_parse_method(
                    ofdb_response['resultat'],
                    search_params
                )
        else:
            return (None, False)

    def _try_sanitize(self, response):
        if response is not None:
            splited = response.splitlines()
            response = ''
            for item in splited:
                if '{"ofdbgw"' in item:
                    response = item
                    break
            try:
                return json.loads(response).get('ofdbgw')
            except (TypeError, ValueError):
                return None

    def _parse_imdb2ofdb_module(self, result, _):
        return (self._build_movie_url([result['ofdbid']]), False)

    def _parse_search_module(self, result, search_params):
        # create similarity matrix for title, check agains german and original
        # title, higher ratio wins
        similarity_map = []
        for result in result['eintrag']:
            # Get the title with the highest similarity ratio:
            ratio = 0.0
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
        return (self._build_movie_url(matches), False)

    def _parse_movie_module(self, result, _):
        result = {
            'original_title': result['alternativ'],
            'title': result['titel'],
            'plot': result['beschreibung'],
            'year': result['jahr'],
            'poster': result['bild'],
            'tagline': result['kurzbeschreibung'],
            'genre': result['genre'],
            'director': [r['name'] for r in result['regie']],
            'countries': result['produktionsland'],
            'rating': result['bewertung']['note'],
            'writer': self._extract_writer(result['drehbuch']),
            'actors': self._get_actor_list(result['besetzung']),
            'imdbid':  'tt{0}'.format(result['imdbid'])

        }
        return (result, True)

    def _extract_writer(self, writer):
        person_list = []
        try:
            for person in writer:
                item = {
                    'name': person.get('name')
                }
                person_list.append(item)
        except (AttributeError, TypeError):
            return []
        return person_list

    def _get_actor_list(self, actors):
        actor_list = []
        try:
            for actor in actors:
                item = {
                    'name': actor.get('name'),
                    'role': actor.get('rolle')
                }
                actor_list.append(item)
        except AttributeError:
            return []
        return actor_list

    def _build_movie_url(self, ofdbid_list):
        url_list = []
        for ofdbid in ofdbid_list:
            url_list.append(
                self._base_url.format(path='movie_json', query=ofdbid)
            )
        return url_list

    @property
    def supported_attrs(self):
        return self._attrs

    def activate(self):
        provider.IMovieProvider.activate(self)
        print('activating... ', __name__)

    def deactivate(self):
        provider.IMovieProvider.deactivate(self)
        print('deactivating... ', __name__)
