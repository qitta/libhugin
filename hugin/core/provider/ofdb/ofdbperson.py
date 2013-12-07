#!/usr/bin/env python
# encoding: utf-8

# stdlib
from urllib.parse import quote

# hugin
from hugin.common.utils.stringcompare import string_similarity_ratio
from hugin.core.provider.ofdb.ofdbcommon import OFDBCommon
import hugin.core.provider as provider


class OFDBPerson(provider.IPersonProvider):
    """ OFDB Person text metadata provider.

    Interfaces implemented according to hugin.provider.interfaces.

    """
    def __init__(self):
        self._priority = 90
        self._common = OFDBCommon()
        self._attrs = [
            'name', 'alternative_names', 'photo', 'placeofbirth', 'imdbid',
            'deathday', 'known_for'
        ]

    def build_url(self, search_params):
        if search_params.name:
            return [
                self._common.base_url.format(
                    path='searchperson_json',
                    query=quote(search_params.name))
            ]

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

        if 'searchperson' in response_type:
            return self._parse_search_module(response, search_params), False

        if 'person' in response_type:
            return self._parse_person_module(response, search_params), True

        return None, True

    def _parse_search_module(self, response, search_params):
        """ Parse a search response. Find high prio result. Build urllist."""
        similarity_map = []
        for response in response['eintrag']:
            if response['wert'].isnumeric():
                # a 'hack' for better name matching, as name string often looks
                # like this 'Emma Roberts (10.02.1991) alias Emma Rose Roberts'
                clean_name, *_ = response['name'].split('(')
                ratio = string_similarity_ratio(
                    clean_name,
                    search_params.name
                )
                similarity_map.append(
                    {'ofdbid': response['wert'],
                     'ratio': ratio, 'name': response['name']}
                )
        # sort by ratio, generate ofdbid list with requestet item count
        similarity_map.sort(
            key=lambda value: value['ratio'],
            reverse=True
        )
        item_count = min(len(similarity_map), search_params.items)
        personids = [item['ofdbid'] for item in similarity_map[:item_count]]
        return self._common.personids_to_urllist(personids)

    def _parse_person_module(self, response, _):
        """ Fill in result_dict. """
        result_dict = {k: None for k in self._attrs}

        #str attrs
        result_dict['name'] = response['name']
        result_dict['imdbid'] = response['imdbid']
        result_dict['deathday'] = response['gestorben']

        #list attrs
        result_dict['alternative_names'] = [response['alternativ']]
        if response['bild']:
            result_dict['photo'] = [(None, response['bild'])]
        return result_dict

    @property
    def supported_attrs(self):
        return self._attrs
