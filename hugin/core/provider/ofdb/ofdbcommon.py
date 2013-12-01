#!/usr/bin/env python
# encoding: utf-8

import json


class OFDBCommon:
    def __init__(self):
        self.base_url = 'http://ofdbgw.home-of-root.de/{path}/{query}'

    def _try_sanitize(self, response):
        splited = response.splitlines()
        response = ''
        for item in splited:
            if '{"ofdbgw"' in item:
                response = item
                break
        try:
            return json.loads(response).get('ofdbgw')
        except (TypeError, ValueError):
            return False

    def _build_urllist_from_idlist(self, ids, path):
        url_list = []
        for ofdbid in ids:
            url = self.base_url.format(path=path, query=ofdbid)
            url_list.append([url])
        return url_list

    def validate_url_response(self, url_response):
        try:
            url, response = url_response.pop()
            return 'ok', (None, None), url, json.loads(response).get('ofdbgw')
        except (TypeError, IndexError):
            return 'critical', (None, True), None, None
        except (ValueError, AttributeError):
            response = self._try_sanitize(response)
            if response is False:
                return 'retry', (None, False), url, response
            else:
                return 'ok', (None, None), url, response

    def personids_to_urllist(self, ids):
        return self._build_urllist_from_idlist(ids, 'person_json')

    def movieids_to_urllist(self, ids):
        return self._build_urllist_from_idlist(ids, 'movie_json')

    def check_response_status(self, response):
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
        status = response['status']['rcode']
        return_code = {
            'valid_response': [0],
            'unknown_error': [1, 2, 5],
            'no_data_found': [4, 9],
            'critical_error': [3]
        }

        if status in return_code['critical_error']:
            return 'critical', (None, True)

        if status in return_code['unknown_error']:
            return 'unknown', (None, False)

        if status in return_code['no_data_found']:
            return 'no_data', ([], True)

        if status in return_code['valid_response']:
            return 'valid', ()
