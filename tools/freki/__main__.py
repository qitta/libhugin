#!/usr/bin/env python
# encoding: utf-8

"""Libhugin analyzer commandline testtool.

Usage:
  freki create <database> <datapath>
  freki list <database>
  freki list <database> attr <attr>
  freki list <database> analyzerdata
  freki list-modifier | list-analyzer
  freki (analyze | modify) plugin <plugin> <database>
  freki (analyze | modify) plugin <plugin> pluginattrs <pluginattrs> <database>
  freki export <database>
  freki -h | --help
  freki --version

Options:
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""

# stdlib
import pprint

# 3rd party
from docopt import docopt
from hugin.analyze.session import Session
from hugin.filewalk import data_import
from hugin.filewalk import data_export
from hugin.filewalk import attr_import_func
from hugin.filewalk import attr_mapping


def list_plugins(plugins):
    for item in plugins:
        print(
            'Name: \t\t{}\nDescription: \t{}\nParameters: \t{}\n'.format(
                item.name, item.description, item.parameters()
            )
        )


def split_pluginattrs(pluginattrs):
    try:
        raw_attrs = pluginattrs.split(',')
        return dict([attr.split('=') for attr in raw_attrs])
    except TypeError:
        return {}


def cluster_kwargs(args, plugin):
    if args['pluginattrs']:
        attrs = split_pluginattrs(args['<pluginattrs>'])
        params = plugin.parameters()
        return {key: constructor(attrs[key]) for key, constructor in params.items()}
    return {}


if __name__ == '__main__':
    args = docopt(__doc__, version="Libhugin 'freki' clitool v0.1")
    MASK = attr_mapping()

    if args['create']:
        s = Session(args['<database>'], attr_mask=MASK)
        path = args['<datapath>']
        metadata = data_import(path)
        for nfofile in metadata:
            s.add(nfofile, attr_import_func)
        s.database_close()

    if args['export']:
        s = Session(args['<database>'], attr_mask=MASK)
        database = s.get_database()
        data_export(database.values())

    if args['list']:
        s = Session(args['<database>'], attr_mask=MASK)
        database = s.get_database()
        for num, movie in enumerate(database.values()):
            if args['attr']:
                print('{}) {}\n{}: \t{}\n'.format(
                    num,
                    movie,
                    args['<attr>'],
                    movie.attributes[args['<attr>']])
                )
            elif args['analyzerdata']:
                print('{}) {}'.format(num, movie))
                pprint.pprint(movie.analyzer_data)
            else:
                print('{}) {}'.format(num, movie))
                pprint.pprint(movie.attributes)
                print("")
        s.database_close()

    if any([args['analyze'], args['modify']]):
        s = Session(args['<database>'], attr_mask=MASK)
        database = s.get_database()
        for movie in database.values():
            if args['analyze']:
                plugin = s.analyzer_plugins(args['<plugin>'])
                plugin.analyze(movie, **cluster_kwargs(args, plugin))
            elif args['modify']:
                plugin = s.modifier_plugins(args['<plugin>'])
                plugin.modify(movie, **cluster_kwargs(args, plugin))
        s.database_close()

    if any([args['list-modifier'], args['list-analyzer']]):
        session = Session('/tmp/temp')
        if args['list-modifier']:
            list_plugins(session.modifier_plugins())
        if args['list-analyzer']:
            list_plugins(session.analyzer_plugins())
