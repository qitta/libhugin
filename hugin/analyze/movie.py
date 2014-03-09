#!/usr/bin/env python
# encoding: utf-8

# stdlib
import os


class Movie:

    def __init__(self, key, nfo, attributes):
        self.key = key
        self.nfo = nfo
        self.attributes = attributes
        self.analyzer_data = {}
        self.comparator_data = {}

    def __repr__(self):
        head, tail = os.path.split(self.key)
        return tail
