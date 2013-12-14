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
        self._template = self._templateEnv.get_template('template.html')

    def convert(self, result):
        if not isinstance(result, Result):
            return None

        data = {'provider': result.provider}
        data.update(result._result_dict)
        if data['poster']:
            size, poster = data.get('poster').pop()
            data['poster'] = poster
        else:
            data['poster'] = 'http://img.ofdb.de/film/na.gif'
        data['actors'] = [a[1] for a in data['actors']]
        return self._template.render(data)
