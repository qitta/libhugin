#!/usr/bin/env python
# encoding: utf-8

# hugin
import hugin.analyze as plugin
from hugin.harvest.session import Session


class PlotChange(plugin.IModifier):

    def __init__(self):
        self._session = Session()

    def modify(self, movie, attr_name='plot', change_to='en'):
        query = self._session.create_query(
            title=movie.attributes.get('title'),
            provider=['tmdbmovie'],
            amount=1,
            language=change_to
        )
        result = self._session.submit(query)
        if result:
            movie.attributes[attr_name] = result.pop()._result_dict.get('plot')

    def modify_all(self, db):
        for movie in db.values():
            self.movie(movie)
