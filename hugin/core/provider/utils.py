#!/usr/bin/env python
# encoding: utf-8


def get_movie_result_dict():
    attrs = [
        'title', 'original_title', 'alternative_titles', 'collection',
        'tagline', 'rating', 'year', 'runtime', 'director', 'writer',
        'certification', 'trailer', 'plot', 'poster', 'fanart', 'countries',
        'actors', 'genres', 'studios', 'imdbid', 'provideridi', ' vote_count'
    ]
    return ({key: None for key in attrs}, 'movie')


def get_person_result_dict():
    attrs = [
        'name', 'photo', 'movies_as_actor', 'movies_as_director',
        'movies_as_writer', 'biography', 'birthday', 'placeofbirth',
        'deathday', 'imdbid', 'providerid', 'role', 'homepage'
    ]
    return ({key: None for key in attrs}, 'person')
