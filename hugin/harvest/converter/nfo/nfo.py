#!/usr/bin/env python
# encoding: utf-8

# hugin
import hugin.harvest.provider as provider

# http://wiki.xbmc.org/index.php?title=NFO_files/movies
# key == nfo attr, item == result_dict key for the specific attr
nfo_dict_map = {
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
        if result and result._result_type == 'movie':
            return self._create_nfo(result)

# Helper functions
    def _create_nfo(self, result):
        for nfo_tag, dict_key in nfo_dict_map.items():
            self._set_value(nfo_dict_map, nfo_tag, dict_key, result)
        return self._base.format(**nfo_dict_map)

    def _set_value(self, nfo_dict_map, nfo_tag, dict_key, result):

        if dict_key in result._result_dict:

            if dict_key in ['genre', 'directors', 'writers', 'countries']:
                nfo_dict_map[nfo_tag] = self._create_multi_tag(
                    result._result_dict[dict_key], nfo_tag
                )
            elif dict_key in ['trailers', 'poster']:
                nfo_dict_map[nfo_tag] = self._extract_tuple_attr(
                    result._result_dict[dict_key]
                )
            else:
                nfo_dict_map[nfo_tag] = result._result_dict[dict_key] or ''
        else:
            if dict_key in ['ACTORS']:
                nfo_dict_map[nfo_tag] = self._create_actor_section(
                    result._result_dict['actors']
                )
            else:
                nfo_dict_map[nfo_tag] = ''

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

    def _extract_tuple_attr(self, result):
        if result:
            for _, item in result:
                return item

    def _open_template(self, template):
        with open(template, 'r') as f:
            return f.read()

if __name__ == '__main__':
    from hugin.harvest.session import Session
    s = Session()
    q = s.create_query(title='Sin', amount=5)
    r = s.submit(q)
    p = Nfo()
    print(r[0])
    print(p.convert(r[0]))
    print('FILM:', r[0])
    print(p.convert(r[0]))
