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

    def validate_response(self, url_response):
        responses = []
        flag = False
        for url, response in url_response:
            try:
                response = json.loads(response)
                responses.append((url, response))
            except (ValueError, TypeError):
                responses.append((url, None))
                flag = True
        return (responses, flag)

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

    def extract_keyvalue_attrs(self, data):
        values = []
        for value in data:
            values.append(value['name'])
        return values

    def build_movie_search_url(self, matches, search_params):
        url_list = self._build_url(matches, search_params, 'movie')
        if len(url_list) == 1:
            return url_list.pop()
        return url_list

    def build_person_search_url(self, matches, search_params):
        url_list = self._build_url(matches, search_params, 'person')
        if len(url_list) == 1:
            return url_list.pop()
        return url_list

    def build_movie_url(self, matches, search_params):
        return self._build_url(matches, search_params, 'movie')

    def build_person_url(self, matches, search_params):
        return self._build_url(matches, search_params, 'person')

    def _build_url(self, matches, search_params, metatype):
        additions = []
        if search_params['search_pictures'] == True:
            additions = ['images']

        urlpaths = {
            'person': ['', 'images', 'movie_credits'],
            'movie': ['', 'keywords', 'credits', 'alternative_titles', 'trailers'] + additions
        }.get(metatype)

        url_list = []
        language = search_params['language'] or ''

        for tmdbid in matches:
            moviepaths = []
            for urlpath in urlpaths:
                if urlpath == '':
                    path = '{url_type}/{tmdbid}{url_path}'
                else:
                    path = '{url_type}/{tmdbid}/{url_path}'

                fullpath = path.format(
                    tmdbid=tmdbid,
                    url_type=search_params['type'],
                    url_path=urlpath
                )
                url = self.baseurl.format(
                        path=fullpath,
                        apikey=self.apikey,
                        query='&language={language}'.format(
                            language=language
                        )
                    )
                moviepaths.append(url)
            url_list.append(moviepaths)
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
