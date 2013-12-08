#!/usr/bin/env python
# encoding: utf-8

""" Common ofdb provider stuff for parsing and extracting values. """

# stdlib
import json
import re


class OFDBCommon:
    def __init__(self):
        self.base_url = 'http://ofdbgw.home-of-root.de/{path}/{query}'

    def _try_sanitize(self, response):
        """ Try to sanitize a broken response containing a valid json doc. """
        splited = response.splitlines()
        response = ''
        for item in splited:
            if re.search('{\s*"ofdbgw"', item):
                response = item
                break
        try:
            return json.loads(response).get('ofdbgw')
        except (TypeError, ValueError):
            return False

    def _build_urllist_from_idlist(self, ids, path):
        """ Build list with urls out of given ids. """
        url_list = []
        for ofdbid in ids:
            url = self.base_url.format(path=path, query=ofdbid)
            url_list.append([url])
        return url_list

    def validate_url_response(self, url_response):
        """ Validate a url-response tuple and load json response. """
        try:
            url, response = url_response.pop()
            return 'ok', (None, None), url, json.loads(response).get('ofdbgw')
        except (ValueError, AttributeError):
            response = self._try_sanitize(response)
            if response is False:
                return 'critical', (None, True), url, response
            else:
                return 'ok', (None, None), url, response

    def personids_to_urllist(self, ids):
        """ Build person provider urllist from person ids. """
        return self._build_urllist_from_idlist(ids, 'person_json')

    def movieids_to_urllist(self, ids):
        """ Build movie provider urllist from person ids. """
        return self._build_urllist_from_idlist(ids, 'movie_json')

    def check_response_status(self, response):
        """
        Validates the http response object status.

        Possible error codes that may apear in the valid json http response::

            0 = Keine Fehler
            1 = Unbekannter Fehler
            2 = Fehler oder Timeout bei Anfrage an IMDB bzw. OFDB
            3 = Keine oder falsche ID angebene
            4 = Keine Daten zu angegebener ID oder Query gefunden
            5 = Fehler bei der Datenverarbeitung
            9 = Wartungsmodus, OFDBGW derzeit nicht verfügbar.

        Returns a state flag and a return value specific to its error code. For
        possible flags an return value tuples see code block below.

        :param response: A json http response object.
        :returns: A tuple containing a status flag and a return value.

        """
        status = response['status']['rcode']
        return_code = {
            'unknown_error': [1, 2, 5],
            'no_data_found': [4, 9],
            'critical_error': [3],
            'valid_response': [0]
        }

        if status in return_code['critical_error']:
            return 'critical', (None, True)

        if status in return_code['unknown_error']:
            return 'unknown', (None, False)

        if status in return_code['no_data_found']:
            return 'no_data', ([], True)

        if status in return_code['valid_response']:
            return 'valid', ()
