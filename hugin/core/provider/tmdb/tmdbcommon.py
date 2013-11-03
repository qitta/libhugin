#!/usr/bin/env python
# encoding: utf-8


def get_api_key():
    return '?api_key=ff9d65f1e39e8a239124b7e098001a57'


def get_base_url():
    return 'http://api.themoviedb.org/3/{path}{apikey}{query}'
