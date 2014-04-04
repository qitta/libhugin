#!/usr/bin/env python
# encoding: utf-8

# hugin
import hugin.harvest.provider as provider

# Simple xbmc nfo converter plugin
# nfo specs taken from http://wiki.xbmc.org/index.php?title=NFO_files/movies


class Nfo(provider.IConverter):

    def __init__(self):
        self._base = self._open_template(
            'hugin/harvest/converter/nfo/nfobase.xml'
        )
        self._filenfo = self._open_template(
            'hugin/harvest/converter/nfo/fileinfo.xml'
        )
        self._actors = self._open_template(
            'hugin/harvest/converter/nfo/actors.xml'
        )
        self.file_ext = '.nfo'

    def convert(self, result):
        if result and result._result_type == 'movie':
            return self._create_nfo(result._result_dict)

# Helper functions
    def _create_nfo(self, result):
        nfo_dict_map = self._get_nfo_result_dict()
        for nfo_tag, dict_key in nfo_dict_map.items():
            self._set_value(nfo_dict_map, nfo_tag, dict_key, result)
        return self._base.format(**nfo_dict_map)

    def _set_value(self, nfo_dict_map, nfo_tag, dict_key, result):

        if dict_key in result:

            if dict_key in ['genre', 'directors', 'writers', 'countries']:
                nfo_dict_map[nfo_tag] = self._create_multi_tag(
                    result[dict_key], nfo_tag
                ) or ' '
            elif dict_key in ['trailers', 'poster', 'collection']:
                nfo_dict_map[nfo_tag] = self._extract_tuple_attr(
                    result.get(dict_key), dict_key
                )
            else:
                nfo_dict_map[nfo_tag] = result[dict_key] or ' '
        else:
            if dict_key in ['ACTORS']:
                nfo_dict_map[nfo_tag] = self._create_actor_section(
                    result['actors']
                )
            else:
                nfo_dict_map[nfo_tag] = ' '

    def _get_nfo_result_dict(self):
        return {
            'title': 'title', 'originaltitle': 'original_title', 'sorttitle':
            'title', 'set': 'collection', 'rating': 'rating', 'year': 'year',
            'top250': 'top250', 'votes': 'vote_count', 'outline': 'outline',
            'plot': 'plot', 'tagline': 'tagline', 'runtime': 'runtime',
            'thumb': 'poster', 'mppa': 'mppa', 'playcount': 'playcount', 'id':
            'imdbid', 'filename': 'filename', 'trailer': 'trailers', 'country':
            'countries', 'genre': 'genre', 'credits': 'writers', 'FILEINFO':
            'FILEINFO', 'director': 'directors', 'ACTORS': 'ACTORS'
        }

    def _create_multi_tag(self, attr, tagname):
        tag = '<{tagname}>{{attr}}</{tagname}>\n'.format(tagname=tagname)
        attrs = []
        if attr:
            for item in attr:
                attrs.append(tag.format(attr=item))
            return ''.join(attrs)

    def _create_actor_section(self, result):
        actors = []
        if result:
            for role, name in result:
                actors.append(self._actors.format(name=name, role=role))
            return ''.join(actors)

    def _extract_tuple_attr(self, result, dict_key):
        if result:
            if dict_key == 'collection':
                return result[0] or ' '
            for size, item in result:
                if dict_key == 'poster' and size == 'original':
                    return item
                elif dict_key == 'trailers':
                    return item or ' '

    def _open_template(self, template):
        with open(template, 'r') as f:
            return f.read()
