#!/usr/bin/env python
# encoding: utf-8

from urllib.request import urlopen
import json


class TMDBConfig:

    _instance = None

    def __init__(self):
        self.apikey = '?api_key=ff9d65f1e39e8a239124b7e098001a57'
        self.baseurl = 'http://api.themoviedb.org/3/{path}{apikey}&query={query}'
        self.image_base_url = ''
        self.poster_sizes = ''
        self.backdrop_sizes = ''
        self.profile_sizes = ''
        self.logo_sizes = ''
        self._load_api_config()

    @staticmethod
    def get_instance():
        if TMDBConfig._instance is None:
            TMDBConfig._instance = TMDBConfig()
        return TMDBConfig._instance

    def _load_api_config(self):
        '''
        Initial tmdb configuration
        '''
        response_bytes = urlopen(
            self.baseurl.format(
                path='configuration',
                apikey=self.apikey,
                query=''
            )
        )
        try:
            response = json.loads(response_bytes.readall().decode('utf-8'))
            response = response.get('images')
            self.image_base_url = '{url}{{size}}{{image}}'.format(
                url=response['base_url']
            )
            self.poster_sizes = [size for size in response['poster_sizes']]
            self.backdrop_sizes = [size for size in response['backdrop_sizes']]
            self.profile_sizes = [size for size in response['profile_sizes']]
            self.logo_sizes = [size for size in response['logo_sizes']]
            response_bytes.close()
        except UnicodeDecodeError as e:
            print(e)

if __name__ == '__main__':
    t = TMDBConfig.get_instance()
    print(t.baseurl)
    print(t.apikey)
    print(t.image_base_url)
