#!/usr/bin/env python
# encoding: utf-8

# stdlib
import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

#hugin
from hugin.utils.stringcompare import string_similarity_ratio
import hugin.harvest.provider as provider


class FILMSTARTSMovie(provider.IMovieProvider):
    """ FILMSTARTS Movie text metadata provider.

    Interfaces implemented according to hugin.provider.interfaces.

    """

    def __init__(self):
        self._base_url = 'http://www.filmstarts.de/suche/?q={}'
        self._movie_url = 'http://www.filmstarts.de{}'
        self._priority = 80
        self._attrs = {
            'title', 'year', 'plot', 'directors', 'actors', 'genre', 'poster'
        }

    def build_url(self, search_params):
        if search_params.title:
            return [self._base_url.format(quote_plus(search_params.title))]

    def parse_response(self, url_response, search_params):

        response = self._identify_response(url_response)

        if response['url'] is None:
            return None, True

        if 'suche' in response['url']:
            result = self._parse_search_module(
                response['main'], search_params
            )
            if result:
                return result, False

        if 'kritiken' in response['url']:
            result = self._parse_movie_module(response, search_params)
            if result:
                return result, True

        return None, True

    def _identify_response(self, url_response):
        responses = {'url': None, 'crew': None, 'main': None}

        for url, html in url_response:
            if html is not None:
                try:
                    if html and 'castcrew' not in url or 'suche' in url:
                        responses['main'] = BeautifulSoup(html)
                        responses['url'] = url
                    if html and 'castcrew' in url:
                        responses['crew'] = BeautifulSoup(html)
                except (TypeError, ValueError) as e:
                    print('Exception in _identify_response filmstarts.', e)
        return responses

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        if result.body.table:
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
                print('AttributeError in _parse_search_module, filmstarts.', e)
                return None

        similarity_map.sort(key=lambda value: value['ratio'], reverse=True)
        item_count = min(len(similarity_map), search_params.amount)

        return self._create_links(similarity_map[:item_count])

    def _create_links(self, similarity_map):
        movielinks = []

        for movie in similarity_map:
            movie_links = []
            movie_links.append(self._movie_url.format(movie['url']))
            movie_links.append(
                self._movie_url.format(
                    movie['url'].replace('.html', '/castcrew.html')
                )
            )
            movielinks.append(movie_links)

        return movielinks

    def _parse_movie_module(self, result, search_params):
        result_dict = {k: None for k in self._attrs}

        #title, year = self._parse_title(result['main'])
        result_dict['title'] = result['main'].h1.get_text()
        result_dict['year'] = self._parse_year(result['main'])

        result_dict['plot'] = self._parse_plot(result['main'])
        result_dict['genre'] = self._parse_genre(result['main'])
        result_dict['directors'] = self._parse_directors(result['main'])

        result_dict['actors'] = self._parse_actors(result['crew'])
        result_dict['poster'] = self._parse_poster(result['main'])

        return result_dict

    def _parse_year(self, response):
        try:
            pattern = re.compile('(\d{4})')
            yearstring = re.search(pattern, response.title.string)
            if yearstring:
                year, *_ = yearstring.groups()
                return int(year)
        except Exception as e:
            print('Exception in _parse_year filmstarts.', e)

    def _parse_plot(self, response):
        plot = response.find(itemprop="description")
        if plot:
            return plot.get_text().replace('\n', '')

    def _parse_poster(self, response):
        try:
            poster_div = response.find("div", {"class": "poster"})
            return [(None, poster_div.find("img").get("src"))]
        except Exception as e:
            print('Unhandeled exception in filmstarts _parse_poster.', e)

    def _parse_genre(self, response):
        genres = []
        for item in response.find_all(itemprop="genre"):
            genres.append(item.get_text())
        return [g.strip() for g in genres]

    def _parse_directors(self, response):
        directors = []
        for item in response.find_all(itemprop="director"):
            directors.append(item.get_text())
        return [d.strip() for d in directors]

    def _parse_actors(self, response):
        actors = []
        for actor in response.find_all(itemprop="actors"):
            if actor.get("itemprop") == 'actors':
                actors.append((None, actor.get_text().replace('\n', '')))
        return [(a, b.strip()) for a, b in actors]

    @property
    def supported_attrs(self):
        return self._attrs
