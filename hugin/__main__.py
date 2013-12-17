#!/usr/bin/env python
# encoding: utf-8

"""Libhugin commandline tool.

Usage:
  cli.py (-t <title>) [-y <year>] [-a <amount>] [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>]
  cli.py (-i <imdbid>) [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>]
  cli.py (-n <name>) [--items <num>] [-p <providers>...] [-c <converter>] [-o <path>]
  cli.py list-provider
  cli.py list-converter
  cli.py list-postprocessing
  cli.py -h | --help
  cli.py --version

Options:
  -t, --title=<title>               Movie title.
  -y, --year=<year>                 Year of movie release date.
  -n, --name=<name>                 Person name.
  -i, --imdbid=<imdbid>             A imdbid prefixed with tt.
  -p, --providers=<providers>       Providers to be used.
  -c, --convert=<converter>         Converter to be used.
  -o, --output=<path>               Output folder for converter result [default: /tmp].
  -a, --amount=<amount>             Amount of items to retrieve.
  -l, --language=<lang>             Language in ISO 639-1 [default: de]
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""

from docopt import docopt
import textwrap
import os


def _get_image(imagelist):
    for imagetuple in imagelist:
        try:
            size, image = imagetuple
            if size == 'original':
                return image
        except:
            return None


def _role_movie_fmt(itemlist):
    fmt = '{} in {}\n'
    result = '\n'
    for item in itemlist:
        rolle, film = item
        result += fmt.format(rolle, film)
    return result


def list_plugins(plugins):
    for item in plugins:
        print(
            'Name: {}\nDescription: {}\n'.format(item.name, item.description)
        )


def wrap_width(text, width=80):
    if text:
        return textwrap.fill(text, width)


def create_movie_cliout(movie):
    fmt = """
# Provider: {provider} ########################################################

* Title: {title} ({year}), imdbid: {imdbid}, raiting: {rating}
* Cover Url: {poster}

Plot: {plot}

* Directors: {directors}
* Genre: {genre}
* Genre {{normlized}}: {genre_norm}

    """
    kwargs = movie._result_dict
    kwargs.setdefault('provider', movie.provider)
    kwargs['poster'] = _get_image(kwargs['poster'])
    kwargs['plot'] = wrap_width(kwargs['plot'])
    return fmt.format(**movie._result_dict)


def create_person_cliout(person):
    fmt = """
# Provider: {provider} ########################################################

Name: {name}
Photo: {photo}
Biography: {biography}
Known for: {known_for}
    """
    kwargs = person._result_dict
    kwargs.setdefault(
        'biography', kwargs.get('biography') or 'No data found.'
    )
    kwargs['biography'] = wrap_width(kwargs['biography'])
    kwargs.setdefault('provider', person.provider)
    if kwargs['known_for']:
        kwargs['known_for'] = _role_movie_fmt(
            kwargs.get('known_for')
        ) or 'No data found.'
    return fmt.format(**person._result_dict)


def output(args, results, session):
    for result in results:
        if args['--convert']:
            converter = session.converter_plugins(args['--convert'])
            if not converter:
                print('{} converter not available.'.format(args['--convert']))
            else:
                filename = '{}{}'.format(result.provider, converter.file_ext)
                path = os.path.join(args['--output'], filename)
                with open(path, 'w') as f:
                    print('** writing result as {} to {}.**'.format(
                        converter.file_ext, path)
                    )
                    f.write(converter.convert(result))
        if result._result_type == 'person':
            print(create_person_cliout(result))
        else:
            print(create_movie_cliout(result))


if __name__ == '__main__':
    from hugin.core import Session
    import pprint

    args = docopt(__doc__, version="Libhugin 'gylfie' clitool v0.1")
    print(args)

    session = Session()

    if args['--imdbid'] or args['--title']:
        if args['--year']:
            args['--year'] = int(args['--year'])
        if args['--providers']:
            providers = args['--providers'].pop().split(',')
        q = session.create_query(
            title=args['--title'],
            year=args['--year'],
            imdbid=args['--imdbid'],
            language=args['--language'],
            providers=providers,
            amount=args['--amount']
        )
        results = session.submit(q)
        output(args, results, session)

    if args['--name']:
        q = session.create_query(name=args['--name'], amount=args['--amount'])
        results = session.submit(q)
        output(args, results, session)

    if args['list-converter']:
        list_plugins(session.converter_plugins())

    if args['list-provider']:
        list_plugins(session.provider_plugins())

    if args['list-postprocessing']:
        list_plugins(session.postprocessing_plugins())
