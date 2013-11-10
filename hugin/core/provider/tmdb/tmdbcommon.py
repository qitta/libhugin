#!/usr/bin/env python
# encoding: utf-8

""" TMDB Provider config and common  attributes. """

from urllib.request import urlopen
import json


class TMDBConfig:

    """ Singleton config class for all tmdb provider plugins. """

    _instance = None

    def __init__(self):
        self.apikey = '?api_key=ff9d65f1e39e8a239124b7e098001a57'
        self.baseurl = 'http://api.themoviedb.org/3/{path}{apikey}&query={query}'
        self.image_base_url = ''
        self._poster_sizes = ''
        self._backdrop_sizes = ''
        self._profile_sizes = ''
        self._logo_sizes = ''
        self._load_api_config()

    @staticmethod
    def get_instance():
        """ Return a instance of tmdb config. """
        if TMDBConfig._instance is None:
            TMDBConfig._instance = TMDBConfig()
        return TMDBConfig._instance

    def _image_sizes_from(self, image_type):
        """
        Read current available image sizes from tmdb config.

        The tmdb config offers imagesizes currently for the four image tpyes
        logo, profile, backdrop and poster.

        :param image_type: Type of image you want to get sizes of.
        :returns: List with available sizes for the given image type.

        """
        types = {
            'logo': self._logo_sizes,
            'profile': self._profile_sizes,
            'backdrop': self._backdrop_sizes,
            'poster': self._poster_sizes
        }
        return types[image_type]

    def get_image_url(self, image, image_type):
        """
        Build a url list for a specific  image type.

        :param image: The image itself
        :param image_type: The image type to build url for.
        :returns: List with image urls.

        """
        url = self.image_base_url
        url_list = []
        image_sizes = self._image_sizes_from(image_type)
        for size in image_sizes:
            url_list.append((size, url.format(size=size, image=image)))
        return url_list

    def extract_keyvalue_attrs(self, data):
        values = []
        for value in data:
            values.append(value['name'])
        return values

    def build_movie_url(self, matches, search_params):
        url_list = []
        language = search_params['language'] or 'en'
        for tmdbid in matches:
            path = '{url_type}/{tmdbid}'.format(
                tmdbid=tmdbid,
                url_type=search_params['type']
            )
            url_list.append(
                self.baseurl.format(
                    path=path,
                    apikey=self.apikey,
                    query='&language={language}'.format(
                        language=language
                    )
                )
            )
        return url_list

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
