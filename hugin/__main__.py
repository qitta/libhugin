#!/usr/bin/env python
# encoding: utf-8

"""Libhugin commandline tool.

Usage:
  cli.py (-t <title>) [-y <year>] [-a <amount>] [-p <providers>...] [-c <converter>] [-o <path>]
  cli.py (-n <name>) [--items <num>] [-p <providers>...] [-c <converter>] [-o <path>]
  cli.py (-i <imdbid>) [-p <providers>...] [-c <converter>] [-o <path>]
  cli.py list-provider
  cli.py list-converter
  cli.py -h | --help
  cli.py --version

Options:
  -t, --title=<title>               Movie title.
  -y, --year=<year>                 Year of movie release date.
  -n, --name=<name>                 Person name.
  -i, --imdbid=<imdbid>             A imdbid prefixed with tt.
  -p, --providers=<providers>       Providers to be useed.
  -c, --convert=<converter>         Converter to be useed.
  -o, --output=<path>               Output folder for converter result.
  -a, --amount=<amount>             Output folder for converter result.
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""
from docopt import docopt


def print_movie_short(resultlist):
    fmt = """
Provider: {p}
Movie:
Title: {m} ({y}), imdbid: {i}, raiting: {r}
Director: {d}
Plot: {plt}

    """
    for movie in resultlist:
        print(
            fmt.format(
                p=movie.provider,
                m=movie._result_dict['title'],
                y=movie._result_dict['year'],
                i=movie._result_dict['imdbid'],
                r=movie._result_dict['rating'],
                d=movie._result_dict['directors'],
                plt=movie._result_dict['plot']
            )
        )


def print_person_short(resultlist):
    pass

if __name__ == '__main__':
    from hugin.core import Session
    import pprint
    arguments = docopt(__doc__, version='Libhugin commandline tool v0.1')

    s = Session()
    if arguments['list-converter']:
        for item in s.converter_plugins():
            print('Name: {}\nDescription: {}\n'.format(item.name, item.description))

    if arguments['list-provider']:
        for item in s.provider_plugins():
            print('Name: {}\nDescription: {}\n'.format(item.name, item.description))

    if arguments['--imdbid']:
        q = s.create_query(imdbid=arguments['--imdbid'])
        print_movie_short(s.submit(q))

    if arguments['--name']:
        q = s.create_query(name=arguments['--name'])
        print_person_short(s.submit(q))

    if arguments['--title']:
        if arguments['--year']:
            year = int(arguments['--year'])
            q = s.create_query(title=arguments['--title'], year=year)
        else:
            q = s.create_query(title=arguments['--title'])
        pprint.pprint(s.submit(q))

    if arguments['--providers']:
        for item in s.provider_plugins():
            out = 'Name: {}\nDescription: {}\nSupported attributes: {}\n'.format(
                item.name, item.description, item.supported_attrs
            )
            print(out)


