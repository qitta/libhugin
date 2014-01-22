#!/usr/bin/env python
# encoding: utf-8

"""Gylfie [libhugin client].

Usage:
  gylfie (-h | --help)
  gylfie person <name> [--use-cache] [--pretty] [--pictures]
  gylfie movie <title> [year] [--use-cache] [--pretty] [--pictures]
  gylfie imdbid <imdbid> [--use-cache] [--pretty] [--pictures]
  gylfie list-provider
  gylfie search -i FILE [--simple]

Options:
  gylfie --version

"""
from docopt import docopt


def search():
    metatype = ''
    for type in types:
        if arguments[type]:
            metatype = type
            break
    if metatype == 'imdbid':
        metatype = 'movie'

    query = session.create_query(
        type=metatype,
        search_text=True,
        cache=arguments['--use-cache'],
        name=arguments['<name>'],
        title=arguments['<title>'],
        imdbid=arguments['<imdbid>'],
        language='de'
    )
    result = session.submit_async(query)
    while result.done() is False:
        pass
    result = result.result()
    for item in result:
        print(item['provider'])
        print('cache used:', item['cache_used'])
        pprint.pprint(item['result'])
        print('#' * 80)

if __name__ == '__main__':
    import pprint
    from hugin import Session

    arguments = docopt(__doc__, version='gylfie [libhugin Client v1.0]')
    # print(arguments)
    types = ['movie', 'person', 'imdbid']
    session = Session()
    if arguments['list-provider']:
        pprint.pprint(session.providers_list())
    else:
        search()
        session.cancel()
