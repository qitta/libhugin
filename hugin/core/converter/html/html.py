#!/usr/bin/env python
# encoding: utf-8

# jinja2
from jinja2 import FileSystemLoader, Environment

# hugin
import hugin.core.provider as provider


class Html(provider.IOutputConverter):

    def __init__(self):
        self._templateLoader = FileSystemLoader('hugin/core/converter/html')
        self._templateEnv = Environment(loader=self._templateLoader)
        self._template = self._templateEnv.get_template('template.html')

    def convert(self, result):
        data = {'provider': result.provider}
        data.update(result._result_dict)
        data['poster'] = '"' + data['poster'].pop()[1] + '"'
        a_list = []
        for actor in data['actors']:
            a_list.append(actor[1])
        data['actors'] = a_list
        return self._template.render(data)

    def __repr__(self):
        return self.name
