#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import os
import glob
import shelve
import xmltodict
from guess_language import guess_language
from collections import Counter

#nfo read helper
def read_attrs(nfofile, mask):
    try:
        with open(nfofile, 'r') as f:
            xml = xmltodict.parse(f.read())
            attributes = {key: None for key in mask.keys()}
            for key, filekey in mask.items():
                attributes[key] = xml['movie'][filekey]
            return attributes
    except Exception as e:
        print('Exception', e)

MASK = {
    'title': 'title',
    'originaltitle': 'originaltitle',
    'year': 'year',
    'plot': 'plot',
    'director': 'director',
    'genre': 'genre'
}

class Session:

    def __init__(self, database, attrs=MASK):
        self._dbname = database
        self._database = shelve.open(self._dbname)
        self._mask = attrs

    def add(self, nfofile):
        if os.path.isdir(nfofile):
            # there is no nfofile, so we get the directory
            movie = Movie(nfofile, None, None)
        else:
            # we have a nfofile, so we can get the directory
            attrs = read_attrs(nfofile, self._mask)
            if attrs is None:
                attrs = {key: None for key in self._mask.keys()}
            movie = Movie(os.path.dirname(nfofile), nfofile, attrs)
        self._database[movie.key] = movie

    def stats(self):
        return "Databse: {}, Entries: {}\n".format(
            self._dbname, len(self._database.keys())
        )

    def database_shutdown(self):
        self._database.close()


class Movie:

    def __init__(self, key, nfo, attributes):
        self.key = key
        self.nfo = nfo
        self._attributes = attributes
        self._analyzer = {}

if __name__ == '__main__':
    s = Session('movie.db')
    path = sys.argv[1]
    c = Counter()
    for moviefolder in os.listdir(path):
        full_movie_path = os.path.join(path, moviefolder)
        nfofile = glob.glob1(full_movie_path, '*.nfo')
        if nfofile == []:
            nfofile = full_movie_path
            c['no_nfo'] += 1
        else:
            nfofile = os.path.join(full_movie_path, nfofile.pop())
        s.add(nfofile)

    import pprint
    for item in dict(s._database).values():
        if item._attributes and item._attributes.get('plot'):
            c[guess_language(item._attributes['plot'])] +=1
    print(s.stats(), c)
    s.database_shutdown()
