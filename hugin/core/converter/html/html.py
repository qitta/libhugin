#!/usr/bin/env python
# encoding: utf-8

# jinja2
from jinja2 import FileSystemLoader, Environment

# hugin
import hugin.core.provider as provider
from hugin.core.provider.result import Result


class Html(provider.IOutputConverter):

    def __init__(self):
        self._templateLoader = FileSystemLoader('hugin/core/converter/html')
        self._templateEnv = Environment(loader=self._templateLoader)
        self._movie_template = self._templateEnv.get_template('mtemplate.html')
        self._person_template = self._templateEnv.get_template('ptemplate.html')
        self.file_ext = '.html'

    def convert(self, result):
        if not isinstance(result, Result):
            return None

        if result._result_type == 'person':
            return self._convert_person(result)

        if result._result_type == 'movie':
            return self._convert_movie(result)

    def _convert_person(self, result):
        data = {'provider': result.provider}
        data.update(result._result_dict)
        if data['photo']:
            size, photo = data.get('photo').pop()
            data['photo'] = photo
        else:
            data['photo'] = 'http://img.ofdb.de/film/na.gif'
        print('inside person')
        return self._person_template.render(data)

    def _convert_movie(self, result):
        data = {'provider': result.provider}
        data.update(result._result_dict)
        if data['poster']:
            size, poster = data.get('poster').pop()
            data['poster'] = poster
        else:
            data['poster'] = 'http://img.ofdb.de/film/na.gif'
        data['actors'] = [a[1] for a in data['actors']]
        return self._movie_template.render(data)
