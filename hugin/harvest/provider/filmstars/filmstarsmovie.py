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

        response = self._identify_response(url_response)

        if response['url_main'] is None:
            return None, True

        if 'suche' in response['url_main']:
            result = self._parse_search_module(
                response['response_main'], search_params
            )
            if result:
                return result, False

        if 'kritiken' in response['url_main']:
            result = self._parse_movie_module(response, search_params)
            if result:
                return result, True

        return None, True

    def _identify_response(self, url_response):
        responses = {
            'url_main': None,
            'responses_crew': None,
            'response_main' :None
        }
        try:
            url_a, response_a = url_response.pop()
            response_a = BeautifulSoup(response_a)

            if len(url_response) > 0:
                url_b, response_b = url_response.pop()
                response_b = BeautifulSoup(response_b)

                if 'castcrew' in url_b:
                    responses['response_main'] = response_a
                    responses['response_crew'] = response_b
                    responses['url_main'] = url_a
                else:
                    responses['response_crew'] = response_a
                    responses['response_main'] = response_b
                    responses['url_main'] = url_a
            else:
                responses['response_main'] = response_a
                responses['url_main'] = url_a
            return responses

        except (TypeError, ValueError) as e:
            print('Unable to parse response.', e)

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

        #return [self._movie_url.format(
        #    item['url'])] for item in similarity_map[:item_count]
        return self._create_links(similarity_map[:item_count])

    def _create_links(self, moviemap):
        movielinks = []
        for movie in moviemap:
            tmp = []
            tmp.append(self._movie_url.format(movie['url']))
            tmp.append(self._movie_url.format(movie['url'].replace('.html', '/castcrew.html')))
            movielinks.append(tmp)
        print(movielinks)
        return movielinks



    def _parse_movie_module(self, result, search_params):
        result_dict = {k: None for k in self._attrs}

        title, year = self._parse_title_year(result['response_main'])
        result_dict['title'] = title
        result_dict['original_title'] = title
        result_dict['plot'] = self._parse_plot(result['response_main'])
        result_dict['genre'] = self._parse_genre(result['response_main'])
        result_dict['directors'] = self._parse_directors(result['response_main'])
        result_dict['year'] = int(year)

        result_dict['actors'] = self._parse_actors(result['response_crew'])

        #to be done
        result_dict['poster'] = "-"
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
        plot = response.find(itemprop="description")
        if plot:
            return plot.get_text().replace('\n', '')

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
