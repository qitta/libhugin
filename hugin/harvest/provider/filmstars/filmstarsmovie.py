#!/usr/bin/env python
# encoding: utf-8

# stdlib
import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

#hugin
from hugin.utils.stringcompare import string_similarity_ratio
import hugin.harvest.provider as provider


class FILMSTARSMovie(provider.IMovieProvider):
    """ FILMSTARS Movie text metadata provider.

    Interfaces implemented according to hugin.provider.interfaces.

    """

    def __init__(self):
        self._base_url = 'http://www.filmstarts.de/suche/?q={}'
        self._movie_url = 'http://www.filmstarts.de/{}'
        self._priority = 80
        self._attrs = {
            'title', 'plot', 'directors', 'year', 'genre'
        }

    def build_url(self, search_params):
        if search_params.title:
            return [self._base_url.format(quote_plus(search_params.title))]

    def parse_response(self, url_response, search_params):

        try:
            url, response = url_response.pop()
            response = BeautifulSoup(response)
        except (TypeError, ValueError) as e:
            print('Unable to parse response.', e)
            return None, True

        if 'suche' in url:
            result = self._parse_search_module(response, search_params)
            if result:
                return result, False

        if 'kritiken' in url:
            result = self._parse_movie_module(response, search_params)
            if result:
                return result, True

        return None, True

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        try:
            for item in result.body.table.find_all("a"):
                if item.get_text() and item.get("href"):
                    title = item.get_text().replace('\n', '')
                    url = item.get("href")
                    ratio = string_similarity_ratio(
                        title,
                        search_params.title
                    )
                    similarity_map.append(
                        {'title': title, 'ratio': ratio, 'url': url}
                    )
        except AttributeError as e:
            print(e)
            return None

        similarity_map.sort(key=lambda value: value['ratio'], reverse=True)
        item_count = min(len(similarity_map), search_params.amount)
        return [[self._movie_url.format(
            item['url'])] for item in similarity_map[:item_count]
        ]

    def _parse_movie_module(self, result, search_params):
        result_dict = {k: None for k in self._attrs}

        title, year = self._parse_title_year(result)
        result_dict['title'] = title
        result_dict['original_title'] = title
        plot = self._parse_plot(result)
        if plot:
            result_dict['plot'] = plot.replace('\n', '')
        result_dict['genre'] = self._parse_genre(result)
        result_dict['directors'] = self._parse_directors(result)
        result_dict['year'] = int(year)

        #to be done
        result_dict['poster'] = "-"
        result_dict['imdbid'] = "-"
        result_dict['rating'] = "-"
        result_dict['genre_norm'] = "-"

        return result_dict

    def _parse_title_year(self, response):
        try:
            pattern = re.compile(r"""   # '\nHer - Film 2013 - FILMSTARTS.de\n'
                            (.+?)\s*    # getting the title
                            \-\s* Film  # the part we want split away
                            \s*         #
                            (\d{4})     # movie release date """, re.X)

            return re.search(pattern, response.title.string).groups()
        except Exception as e:
            print('Unhandled parse_error exception in filmstars.', e)

    def _parse_plot(self, response):
        for item in response.find_all(itemprop="description"):
            return item.get_text()

    def _parse_genre(self, response):
        genres = []
        for item in response.find_all(itemprop="genre"):
            genres.append(item.get_text())
        return genres

    def _parse_directors(self, response):
        directors = []
        for item in response.find_all(itemprop="director"):
            directors.append(item.get_text())
        return directors

    @property
    def supported_attrs(self):
        return self._attrs
