#!/usr/bin/env python
# encoding: utf-8

#3rd party
from lxml import etree

# hugin
import hugin.harvest.provider as provider
from hugin.harvest.provider.result import Result

# http://wiki.xbmc.org/index.php?title=NFO_files/movies

value_dict = {
    'title': 'title', 'originaltitle': 'original_title', 'sorttitle': 'title',
    'set': 'collection', 'rating': 'rating', 'year': 'year', 'top250':
    'top250', 'votes': 'vote_count', 'outline': 'outline', 'plot': 'plot',
    'tagline': 'tagline', 'runtime': 'runtime', 'thumb': 'poster', 'mppa':
    'mppa', 'playcount': 'playcount', 'id': 'imdbid', 'filename': 'filename',
    'trailer': 'trailers', 'country': 'countries', 'genre': 'genre', 'credits':
    'writers', 'FILEINFO': 'FILEINFO', 'director': 'directors', 'ACTORS':
    'ACTORS'
}


class Nfo(provider.IOutputConverter):

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
        if not isinstance(result, Result):
            return None

        if result._result_type == 'movie':
            return self._create_nfo(result)

    def _create_nfo(self, result):
        for nfo_tag, dict_key in value_dict.items():
            self._set_value(value_dict, nfo_tag, dict_key, result)
        return self._base.format(**value_dict)

    def _set_value(self, value_dict, nfo_tag, dict_key, result):

        if dict_key in result._result_dict:
            print(dict_key)

            if dict_key in ['genre', 'directors', 'writers', 'countries']:
                value_dict[nfo_tag] = self._create_multi_tag(
                    result._result_dict[dict_key], nfo_tag
                )
            elif dict_key in ['trailers', 'poster']:
                value_dict[nfo_tag] = self._extract_attr_tuple(
                    result._result_dict[dict_key]
                )
            else:
                value_dict[nfo_tag] = result._result_dict[dict_key] or ''
        else:
            if dict_key in ['ACTORS']:
                value_dict[nfo_tag] = self._create_actor_section(
                    result._result_dict['actors']
                )
            else:
                value_dict[nfo_tag] = ''

    def _create_multi_tag(self, attr, tagname):
        tag = '<{tagname}>{{attr}}</{tagname}>\n'.format(tagname=tagname)
        attrs = []
        for item in attr:
            attrs.append(tag.format(attr=item))
        return ''.join(attrs)

    def _create_actor_section(self, result):
        actors = []
        for role, name in result:
            actors.append(self._actors.format(name=name, role=role))
        return ''.join(actors)

    def _extract_attr_tuple(self, result):
        for _, item in result:
            return item

    def _open_template(self, template):
        with open(template, 'r') as f:
            return f.read()
