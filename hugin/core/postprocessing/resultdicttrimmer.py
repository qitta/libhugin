#!/usr/bin/env python
# encoding: utf-8

""" Postprocessing module to create a custom result out of found results. """

# hugin
import hugin.core.provider as provider
from hugin.core.provider.result import Result


class ResultDictTrimmer(provider.IPostprocessing):

    def __init__(self):
        self._strattrs = set([
            'title', 'original_title', 'plot', 'imdbid', 'rating',
            'providerid', 'tagline', 'outline'
        ])
        self._listattrs = set([
            'directors', 'writers', 'countries', 'genre',
            'genre_norm', 'collection', 'studios', 'keywords'
        ])
        self._tuplestrattrs = set([
            'fanart', 'crew', 'actors', 'poster', 'fanart', 'trailers',
            'alternative_titles'
        ])

    def trim_result(self, result):
        if result._result_dict:
            if result._result_type == 'movie':
                self._trim_movie_result(result._result_dict)
            elif result._result_type == 'person':
                self._trim_person_result(result._result_dict)

    def trim_result_list(self, results):
        for result in results:
            self.trim_result(result)

    def _trim_movie_result(self, result_dict):
        keys = set(result_dict.keys())

        strattrs = keys & self._strattrs
        for attr in strattrs:
            if result_dict.get(attr):
                result_dict[attr] = result_dict[attr].strip()

        listattrs = keys & self._listattrs
        self._trim_str_list(listattrs, result_dict)

        tuplestrattrs = keys & self._tuplestrattrs
        self._trim_tuple_str_list(tuplestrattrs, result_dict)

    def _trim_str_list(self, attrs, resultdict):
        for attr in attrs:
            if resultdict[attr]:
                resultdict[attr] = [v.strip() for v in resultdict[attr] if v]

    def _trim_tuple_str_list(self, attrs, resultdict):
        print('striping tupleattrs', attrs)
        for attr in attrs:
            if resultdict[attr]:
                resultdict[attr] = list(
                    map(self._tuple_strip, resultdict[attr])
                )

    def _tuple_strip(self, attrtuple):
        item_strip = lambda x: x.strip() if x else None
        return tuple(map(item_strip, attrtuple))

    def _trim_person_result(self, resultdict):
        pass

    def __repr__(self):
        return '{} I am a result dict trimmer.'.format(self.name)

if __name__ == '__main__':
    rdt = ResultDictTrimmer()
    rd = {
        'title': '    katzen   ',  # str testattr
        'rating': None,  # str testattr
        'genre': ['   comedy', 'action   '],  # str list testatter
        'alternative_titles': ['   comedy', None],  # str list testatter
        'actors': [
            ('wolle  ', '  hans peter'), ('jürgen', 'soße'), (None, None)
        ]
    }
    q = {'type': 'movie'}
    r = Result('prov', q, rd, 8)
    import pprint
    print('before')
    pprint.pprint(r._result_dict)
    rdt.trim_result(r)
    print()
    print('after')
    pprint.pprint(r._result_dict)
