#!/usr/bin/env python
# encoding: utf-8

"""Libhugin analyzer commandline testtool.

Usage:
  freki --create <database> <datapath>
  freki list-modifier
  freki list-analyzer
  freki list-comparator
  freki analyze <item>
  freki modify <item>
  freki compare <item>
  freki -h | --help
  freki --version

Options:
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""

# stdlib
import os
import sys
import glob
import xmltodict
import json
from collections import Counter

# 3rd party
from guess_language import guess_language
from docopt import docopt
from hugin.analyze.session import Session

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
            xml = xmltodict.parse(f.read())
            print(mask.keys())
            attributes = {key: None for key in mask.keys()}
            for key, filekey in mask.items():
                attributes[key] = xml['movie'][filekey]
            return attributes
    except Exception as e:
        print('Exception', e)


def stats(session):
    print(session.stats())


def list_plugins(plugins):
    for item in plugins:
        print(
            'Name: \t\t{}\nDescription: \t{}\n'.format(
                item.name, item.description
            )
        )


def modify(plugin, data):
    pass


def analyze(plugin, data):
    pass


def compare(plugin, data):
    pass


if __name__ == '__main__':
    from hugin.analyze.session import Session
    args = docopt(__doc__, version="Libhugin 'freki' clitool v0.1")

    print(args)

    if args['--create']:
        s = Session(args['<database>'], attr_mask=MASK)
        path = args['<datapath>']
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

    #if args['list-modifier']:
    #    list_plugins(session.modifier_plugins())

    #if args['list-analyzer']:
    #    list_plugins(session.analyzer_plugins())

    #if args['list-comparator']:
    #    list_plugins(session.comparator_plugins())


