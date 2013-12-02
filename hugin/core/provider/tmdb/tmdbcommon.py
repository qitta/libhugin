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

    def validate_url_response(self, url_response):
        try:
            url, response = url_response.pop()
            return url, json.loads(response)
        except (ValueError, TypeError, IndexError, AttributeError):
            return url, None


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
        }.get(image_type)

        return types

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

    def extract_image_by_type(self, response, image_type):
        images = []
        if response.get('images'):
            for image_entry in response['images'][image_type]:
                images += self.get_image_url(
                    image_entry['file_path'], image_type[:-1]
                )
        return images

    def extract_keyvalue_attrs(self, data, key_a=None, key_b=None):
        values = []
        for value in data:
            if key_b:
                values.append((value[key_a], value[key_b]))
            else:
                values.append(value[key_a])
        return values

    def build_movie_search_url(self, matches, search_params):
        return self._build_url(matches, search_params, 'movie').pop()

    def build_person_search_url(self, matches, search_params):
        return self._build_url(matches, search_params, 'person').pop()

    def build_movie_urllist(self, matches, search_params):
        return self._build_url(matches, search_params, 'movie')

    def build_person_urllist(self, matches, search_params):
        return self._build_url(matches, search_params, 'person')

    def _build_url(self, matches, search_params, metatype):
        attrs = {
            'person': ['movie_credits'],
            'movie': ['keywords', 'credits', 'alternative_titles', 'trailers']
        }.get(metatype)

        if search_params['search_pictures'] is True:
            attrs += ['images']

        append_to_response = ','.join(attrs)
        language = search_params['language'] or ''

        url_list = []
        for tmdbid in matches:
            fullpath = '{url_type}/{tmdbid}'.format(
                tmdbid=tmdbid,
                url_type=search_params['type']
            )
            url = self.baseurl.format(
                path=fullpath,
                apikey=self.apikey,
                query='&append_to_response={attrs}&language={language}'.format(
                    attrs=append_to_response,
                    language=language
                )
            )
            url_list.append([url])
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
            self._poster_sizes = response['poster_sizes']
            self._backdrop_sizes = response['backdrop_sizes']
            self._profile_sizes = response['profile_sizes']
            self._logo_sizes = response['logo_sizes']
            response_bytes.close()
        except UnicodeDecodeError as e:
            print(e)

if __name__ == '__main__':
    t = TMDBConfig.get_instance()
    print(t.baseurl)
    print(t.apikey)
    print(t.image_base_url)
    print(t._profile_sizes)
