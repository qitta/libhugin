#!/usr/bin/env python
# encoding: utf-8


from core.provider import IMovieMetadata
from core.provider import IMovieCover


class IMDB(IMovieMetadata):
    name = 'IMDB Movie Provider'

    def __init__(self):
        print('Default Metadata Plugin created.')

    def search_movie(self, movie, year):
        pass

    def activate(self):
        IMovieMetadata.activate(self)
        print('activating...')

    def deactivate(self):
        IMovieMetadata.activate(self)
        print('deactivating...')


class IMDBCover(IMovieCover):

    def __init__(self):
        print('Cover Plugin created.')
