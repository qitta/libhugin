#!/usr/bin/env python
# encoding: utf-8

# stdlib
from collections import Counter
import os
import sys
import glob
import xmltodict
import json

# 3rd party
from guess_language import guess_language

# hugin
from hugin.analyze.session import Session

MASK = {
    'title': 'title', 'originaltitle': 'original_title', 'year': 'year',
    'plot': 'plot', 'director': 'directors', 'genre': 'genre_norm'
}


#nfo read helper
def read_attrs(nfofile, mask):
    try:
        with open(nfofile, 'r') as f:
            #xml = xmltodict.parse(f.read())
            xml = json.loads(f.read())
            attributes = {key: None for key in mask.keys()}
            for key, filekey in mask.items():
                attributes[key] = xml[filekey]
            return attributes
    except Exception as e:
        print('Exception', e)


if __name__ == '__main__':
    s = Session('movie.db', attr_mask=MASK)
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
        s.add(nfofile, read_attrs)

    for item in dict(s._database).values():
        if item.attributes and item.attributes.get('plot'):
            c[guess_language(item.attributes['plot'])] += 1
    print(s.stats(), c)
    s.database_shutdown()
