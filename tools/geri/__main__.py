#!/usr/bin/env python
# encoding: utf-8

"""Libhugin commandline tool.

Usage:
  geri (-t <title>) [-y <year>] [-a <amount>] [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>] [-P <pm>]  [-r <processor>] [-f <pfile>] [-L]
  geri (-i <imdbid>) [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>] [-r <processor>] [-f <pfile>] [-L]
  geri (-n <name>) [--items <num>] [-p <providers>...] [-c <converter>] [-o <path>]
  geri list-provider
  geri list-converter
  geri list-postprocessing
  geri -h | --help
  geri --version

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
  -L, --lookup-mode                 Does a title -> imdbid lookup.
  -f, --profile-file=<pfile>        User specified profile.
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""

# stdlib
from collections import defaultdict
import pprint
import textwrap
import os

# 3rd party libs
from docopt import docopt

# hugin
import hugin.harvest.provider as hugin


def list_plugins(plugins):
    for item in plugins:
        print(
            'Name: {}\nDescription: {}\n'.format(item.name, item.description)
        )


def _format_movie(kwargs):
    kwargs['plot'] = _plot_wrap_width(kwargs['plot'])
    kwargs['actors'] = _actor_format(kwargs['actors'])
    kwargs['poster'] = _poster_format(kwargs['poster'])
    return kwargs


def _plot_wrap_width(text, width=72, subsequent_indent=""):
    if text:
        return textwrap.fill(
            text,
            width,
            subsequent_indent=subsequent_indent,
            fix_sentence_endings=True
        )


def _poster_format(imagelist):
    images = defaultdict(list)
    if imagelist:
        for imagetuple in imagelist:
            try:
                size, image = imagetuple
                images[str(size)].append(image)
            except ValueError as e:
                print(e)
        return pprint.pformat(images)


def _actor_format(itemlist):
    fmt = '{} ({}), '
    result = ''
    if itemlist:
        for item in itemlist:
            rolle, name = item
            result += fmt.format(name, rolle)
        return result


def _format_person(kwargs):
    kwargs['photo'] = pprint.pformat(kwargs['photo'])
    return kwargs


def _format_result(num, result):
    attrs = {
        'person': {
            'mask': hugin.PERSON_ATTR_MASK,
            'prof': 'tools/geri/person.mask',
            'formatter': _format_person
        },
        'movie': {
            'mask': hugin.MOVIE_ATTR_MASK,
            'prof': 'tools/geri/movie.mask',
            'formatter': _format_movie
        }
    }
    result_type = attrs[result._result_type]
    kwargs = {key: None for key in result_type['mask']}
    fmt = _read_mask(result_type['prof'])
    kwargs.update(result._result_dict)
    return fmt.format(**result_type['formatter'](kwargs))

def _read_mask(filename):
    with open(filename, 'r') as f:
        return f.read()

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

        result._result_dict.setdefault('num', num)
        result._result_dict.setdefault('provider', result.provider)
        print(_format_result(num, result))


if __name__ == '__main__':
    from hugin.harvest import Session

    args = docopt(__doc__, version="Libhugin 'geri' clitool v0.1")

    session = Session()
    if args['--imdbid'] or args['--title']:
        if args['--year']:
            args['--year'] = int(args['--year'])
        if args['--providers']:
            args['--providers'] = args['--providers'].pop().split(',')
        if args['--amount']:
            args['--amount'] = int(args['--amount'])
        q = session.create_query(
            id_title_lookup=args['--lookup-mode'],
            title=args['--title'],
            year=args['--year'],
            imdbid=args['--imdbid'],
            language=args['--language'],
            providers=args['--providers'],
            fuzzysearch=args['--predator-mode'],
            amount=args['--amount'],
            remove_invalid=False

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
