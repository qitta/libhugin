#!/usr/bin/env python
# encoding: utf-8

#!/usr/bin/env python
# encoding: utf-8

"""Libhugin analyzer commandline testtool.

Usage:
  ferki list-modifier
  ferki list-analyzer
  ferki list-comparator
  ferki -h | --help
  ferki --version

Options:
  -v, --version                     Show version.
  -h, --help                        Show this screen.

"""

from docopt import docopt


def list_plugins(plugins):
    for item in plugins:
        print(
            'Name: {}\nDescription: {}\n'.format(item.name, item.description)
        )

if __name__ == '__main__':
    from hugin.analyze.session import Session
    session = Session('/tmp/ferki-temp-db')

    args = docopt(__doc__, version="Libhugin 'ferki' clitool v0.1")

    if args['list-modifier']:
        list_plugins(session.modifier_plugins())

    if args['list-analyzer']:
        list_plugins(session.analyzer_plugins())

    if args['list-comparator']:
        list_plugins(session.comparator_plugins())
