#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import glob
import xmltodict

#hugin
from hugin.core.cache import Cache


class Session:

    def __init__(self, database):
        self._database = Cache()
        self._database.open(cache_name=database)

    def add(self, key, value):
        self._database.write(key, value)

    def get(self, key):
        return self._database.read(key)

    def database_shutdown(self):
        self._database.close()


class Movie:
    def __init__(self, key):
        self.key = key
        self._nfo = glob.glob1(key, '*.nfo')
        self._dictrepr = self._load()

    def _load(self):
        if self._nfo:
            try:
                self._nfo = self._nfo.pop()
                full_path = os.path.join(self.key, self._nfo)
                with open(full_path, 'r') as f:
                    return xmltodict.parse(f.read())
            except Exception as e:
                print(e)


class MovieFileWalker:
    def __init__(self):
        self._path = None
        self._movies = None
        self._movie_objs = []

    def walk(self, path):
        self._path = path
        self._movies = os.listdir(path)
        for key in [os.path.join(self._path, m) for m in self._movies]:
            self._movie_objs.append(Movie(key))

    def get_movies(self):
        return self._movie_objs


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('no movie path given.')

    if os.path.exists(sys.argv[1]):
        s = Session('movie.db')
        m = MovieFileWalker()
        m.walk(sys.argv[1])
        for item in m.get_movies():
            print(item._dictrepr.get('movie').get('title'))
        s.database_shutdown()

    print('invalid or no path given.')
