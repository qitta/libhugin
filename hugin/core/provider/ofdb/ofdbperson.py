#!/usr/bin/env python
# encoding: utf-8


import hugin.core.provider as provider
from hugin.common.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.ofdb.ofdbcommon import OFDBCommon

from urllib.parse import quote


class OFDBPerson(provider.IPersonProvider):
    def __init__(self):
        self._priority = 90
        self._common = OFDBCommon()
        self._attrs = [
            'name', 'alternative_names', 'photo', 'placeofbirth', 'imdbid',
            'deathday', 'known_for'
        ]

    def build_url(self, search_params):
        if search_params['name']:
            return [
                self._common.base_url.format(
                    path='searchperson_json',
                    query=quote(search_params['name']))
            ]

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

        select_parse_method = {
            'person': self._parse_person_module,
            'searchperson': self._parse_search_module
        }.get(response['status']['modul'])

        if select_parse_method:
            return select_parse_method(
                response['resultat'],
                search_params
            )

        return None, True

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        for result in result['eintrag']:
            if result['wert'].isnumeric():
                # a 'hack' for better name matching, as name string often looks
                # like this 'Emma Roberts (10.02.1991) alias Emma Rose Roberts'
                clean_name, *_ = result['name'].split('(')
                ratio = string_similarity_ratio(
                    clean_name,
                    search_params['name']
                )
                similarity_map.append(
                    {'ofdbid': result['wert'],
                     'ratio': ratio, 'name': result['name']}
                )
        # sort by ratio, generate ofdbid list with requestet item count
        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params['items'])
        matches = [item['ofdbid'] for item in similarity_map[:item_count]]
        return (self._common.personids_to_urllist(matches), False)

    def _parse_person_module(self, result, _):
        result_dict = {k: None for k in self._attrs}

        #str attrs
        result_dict['name'] = result['name']
        result_dict['imdbid'] = result['imdbid']
        result_dict['deathday'] = result['gestorben']

        #list attrs
        result_dict['alternative_names'] = [result['alternativ']]
        if result['bild']:
            result_dict['photo'] = list((None, result['bild']))

        return result_dict, True

    @property
    def supported_attrs(self):
        return self._attrs
