#!/usr/bin/env python
# encoding: utf-8


def get_movie_result_dict():
    attrs = [
        'title', 'original_title', 'alternative_titles', 'set', 'tagline',
        'rating', 'year', 'runtime', 'director', 'writer', 'certification',
        'trailer', 'plot', 'poster', 'fanart', 'countries', 'actors', 'genres',
        'studios', 'imdbid', 'vote_count'
    ]
    return ({key: None for key in attrs}, 'movie')


def get_poster_result_dict():
    attrs = [
        'title', 'original_title', 'year', 'imdbid', 'poster'
    ]
    return ({key: None for key in attrs}, 'poster')


def get_fanart_result_dict():
    attrs = [
        'title', 'original_title', 'year', 'imdbid', 'fanart'
    ]
    return ({key: None for key in attrs}, 'fanart')


def get_person_result_dict():
    attrs = [
        'name', 'photo', 'movies', 'biography', 'birthday', 'placeofbirth',
        'deathday', 'imdbid'
    ]
    return ({key: None for key in attrs}, 'person')
