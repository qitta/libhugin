#!/usr/bin/env python
# encoding: utf-8

"""Libhugin analyzer commandline testtool.

Usage:
  freki create <database> <datapath>
  freki list <database>
  freki list <database> item <item>
  freki list <database> analyzer <modifier>
  freki list-modifier | list-analyzer
  freki (analyze | modify) <plugin> <database>
  freki -h | --help
  freki --version

Options:
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""

# stdlib
import os
import glob
import xmltodict
from collections import Counter

# 3rd party
from guess_language import guess_language
from docopt import docopt
from hugin.analyze.session import Session

MASK = {
    'title': 'title', 'originaltitle': 'originaltitle', 'year': 'year',
    'plot': 'plot', 'director': 'director', 'genre': 'genre'
}


#nfo read helper
def read_attrs(nfo_file, mask):
    try:
        with open(nfo_file, 'r') as f:
            xml = xmltodict.parse(f.read())
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
    plugin.analyze(movie)


def compare(plugin, data):
    pass


if __name__ == '__main__':
    args = docopt(__doc__, version="Libhugin 'freki' clitool v0.1")

    if args['create']:
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

    if args['list']:
        s = Session(args['<database>'])
        database = s.get_database()
        for movie in database.values():
            if args['item']:
                print(movie, movie.attributes[args['<item>']])
            else:
                import pprint
                print(movie)
                pprint.pprint(movie.analyzer_data)
                print("")

    if args['analyze'] or args['modify']:
        s = Session(args['<database>'])
        database = s.get_database()
        for movie in database.values():
            plugin = s.analyzer_plugins(args['<plugin>'])
            plugin.analyze(movie)
        s.database_shutdown()

    if args['list-modifier']:
        session = Session('/tmp/temp')
        list_plugins(session.modifier_plugins())

    if args['list-analyzer']:
        session = Session('/tmp/temp')
        list_plugins(session.analyzer_plugins())
