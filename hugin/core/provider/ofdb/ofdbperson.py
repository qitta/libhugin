#!/usr/bin/env python
# encoding: utf-8

""" OFDB Person text provider. """

from urllib.parse import quote
import json

import hugin.core.provider as provider
from hugin.common.utils.stringcompare import string_similarity_ratio


class OFDBPerson(provider.IPersonProvider):
    def __init__(self):
        self._priority = 90
        self._base_url = 'http://ofdbgw.home-of-root.de/{path}/{query}'
        self._attrs = {
            'name': 'name',
            'alternative_name': 'alternativ',
            'photo': 'bild',
            'birthday': None,
            'placeofbirth': '',
            'imdbid': 'imdbid',
            'providerid': None,
            'homepage': None,
            'deathday': 'gestorben',
            'popularity': None,
            'biography': None,
            'known_for': '__known_for'
        }

    def build_url(self, search_params):
        if search_params['name'] is None:
            return None
        path, query = 'searchperson_json', quote(search_params['name'])
        return [self._base_url.format(path=path, query=query)]

    def parse_response(self, url_response, search_params):
        """
        Parse ofdb response.

        0 = Keine Fehler
        1 = Unbekannter Fehler
        2 = Fehler oder Timeout bei Anfrage an IMDB bzw. OFDB
        3 = Keine oder falsche ID angebene
        4 = Keine Daten zu angegebener ID oder Query gefunden
        5 = Fehler bei der Datenverarbeitung
        9 = Wartungsmodus, OFDBGW derzeit nicht verfügbar.

        """

        if url_response is None:
            return (None, False)

        try:
            first_element, *_ = url_response
            _, response = first_element
        except ValueError:
            return (None, False)

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
                'person': self._parse_person_module,
                'searchperson': self._parse_search_module
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

    def _parse_search_module(self, result, search_params):

        similarity_map = []
        for result in result['eintrag']:
            if result['wert'].isnumeric():
                ratio = string_similarity_ratio(
                    result['name'],
                    search_params['name']
                )
                similarity_map.append(
                    {'ofdbid': result['wert'],
                     'ratio': ratio}
                )

        # sort by ratio, generate ofdbid list with requestet item count
        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])
        matches = [item['ofdbid'] for item in similarity_map[:item_count]]
        return (self._build_person_url(matches), False)

    def _parse_person_module(self, result, _):
        result_dict = {}
        for key, value in self._attrs.items():
            if value and not value.startswith('__'):
                result_dict[key] = result[value]
        return (result_dict, True)

    def _build_person_url(self, ofdbid_list):
        url_list = []
        for ofdbid in ofdbid_list:
            url = self._base_url.format(path='person_json', query=ofdbid)
            url_list.append([url])
        return url_list

    @property
    def supported_attrs(self):
        return [k for k, v in self._attrs.items() if v is not None]
