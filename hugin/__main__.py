#!/usr/bin/env python
# encoding: utf-8

"""Libhugin commandline tool.

Usage:
  gylfie (-t <title>) [-y <year>] [-a <amount>] [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>] [-P <pm>]  [-r <processor>] [-f <pfile>]
  gylfie (-i <imdbid>) [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>] [-r <processor>] [-f <pfile>]
  gylfie (-n <name>) [--items <num>] [-p <providers>...] [-c <converter>] [-o <path>]
  gylfie list-provider
  gylfie list-converter
  gylfie list-postprocessing
  gylfie -h | --help
  gylfie --version

Options:
  -t, --title=<title>               Movie title.
  -y, --year=<year>                 Year of movie release date.
  -n, --name=<name>                 Person name.
  -i, --imdbid=<imdbid>             A imdbid prefixed with tt.
  -p, --providers=<providers>       Providers to be used.
  -c, --convert=<converter>         Converter to be used.
  -r, --postprocess=<processor>     Postprocessor to be used.
  -o, --output=<path>               Output folder for converter result [default: /tmp].
  -a, --amount=<amount>             Amount of items to retrieve.
  -l, --language=<lang>             Language in ISO 639-1 [default: de]
  -P, --predator-mode               The magic 'fuzzy search' mode.
  -f, --profile-file=<pfile>        User specified profile.
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""

from docopt import docopt
import textwrap
import os


def _get_image(imagelist):
    if imagelist:
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


def wrap_width(text, width=72, subsequent_indent="              "):
    if text:
        return textwrap.fill(text, width, subsequent_indent=subsequent_indent,fix_sentence_endings=True)


def create_movie_cliout(num, movie):
#    fmt = """
#{num}) Provider: {provider}
#
#Title       : {title} ({year}), imdbid: {imdbid}, raiting: {rating}
#Cover Url   : {poster}
#
#Plot        : {plot}
#
#Directors   : {directors}
#Genre       : {genre}
#Genre [norm]: {genre_norm}
#
#    """
    fmt = _load_profile('hugin/movie.mask')
    kwargs = movie._result_dict
    kwargs.setdefault('num', num)
    kwargs.setdefault('provider', movie.provider)
    kwargs['poster'] = _get_image(kwargs['poster'])
    kwargs['plot'] = wrap_width(kwargs['plot'])
    return fmt.format(**movie._result_dict)


def create_person_cliout(num, person):
    fmt = _load_profile('hugin/person.mask')
    kwargs = person._result_dict
    kwargs.setdefault('num', num)
    kwargs.setdefault(
        'biography', kwargs.get('biography') or 'No data found.'
    )
    kwargs['biography'] = wrap_width(kwargs['biography'])
    kwargs['photo'] = _get_image(kwargs['photo'])
    kwargs.setdefault('provider', person.provider)
    if kwargs['known_for']:
        kwargs['known_for'] = _role_movie_fmt(
            kwargs.get('known_for')
        ) or 'No data found.'
    return fmt.format(**person._result_dict)


def _load_profile(filename):
    with open(filename, 'r') as f:
        return eval(f.read())

def output(args, results, session):
    if args['--postprocess']:
        processor = session.postprocessing_plugins(args['--postprocess'])
        if processor:
            if args['--profile-file']:
                profile = _load_profile(args['--profile-file'])
                pp_result = processor.process(results=results, profile=profile)
            else:
                pp_result = processor.process(results)
            if pp_result:
                results += pp_result
    for num, result in enumerate(results, start=1):
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
            print(create_person_cliout(num, result))
        else:
            print(create_movie_cliout(num, result))


if __name__ == '__main__':
    from hugin.harvest import Session
    import pprint

    args = docopt(__doc__, version="Libhugin 'gylfie' clitool v0.1")

    session = Session()
    if args['--imdbid'] or args['--title']:
        if args['--year']:
            args['--year'] = int(args['--year'])
        if args['--providers']:
            args['--providers'] = args['--providers'].pop().split(',')
        if args['--amount']:
            args['--amount'] = int(args['--amount'])
        q = session.create_query(
            title=args['--title'],
            year=args['--year'],
            imdbid=args['--imdbid'],
            language=args['--language'],
            providers=args['--providers'],
            fuzzysearch=args['--predator-mode'],
            amount=args['--amount'],

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
