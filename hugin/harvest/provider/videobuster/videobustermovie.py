#!/usr/bin/env python
# encoding: utf-8

# stdlib
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

#hugin
from hugin.utils.stringcompare import string_similarity_ratio
import hugin.harvest.provider as provider


class VIDEOBUSTERMovie(provider.IMovieProvider):
    """ VIDEOBUSTER Movie text metadata provider.

    Interfaces implemented according to hugin.provider.interfaces.

    """

    def __init__(self):
        self._base_url = 'https://www.videobuster.de/titlesearch.php?tab_search_content=movies&view=title_list_view_option_list&search_title={}'
        self._movie_url = 'https://www.videobuster.de{}?content_type_idnr=1&tab=details'
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

        if 'titlesearch.php' in url:
            result = self._parse_search_module(response, search_params)
            if result:
                return result, False

        if 'titledtl.php' in url:
            print(url)
            result = self._parse_movie_module(response, search_params)
            if result:
                return result, True

        return None, True

    def _parse_search_module(self, result, search_params):
        similarity_map = []
        try:
            for item in result.find_all("div", {"class":"name"}):
                if item.get_text() and item.find("a").get("href"):
                    title = item.get_text()
                    url, _ = item.find("a").get("href").split('?', maxsplit=1)
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
        result_dict['title'] = self._strip_attr(
            self._extract_item(result, 'Originaltitel')
        )
        result_dict['plot'] = self._strip_attr(result.find(
            "div", {"class": "txt movie_description"}).get_text()
        )

        result_dict['original_title'] = self._strip_attr(result_dict['title'])

        result_dict['genre'] = self._strip_attr(
            self._extract_item(result, 'genre').split(',')
        )
        result_dict['directors'] = self._strip_attr(
            self._extract_item(result, 'regie').split(',')
        )

        country, year = self._strip_attr(
            self._extract_item(result, 'produktion').rsplit(maxsplit=1)
        )

        result_dict['year'], result_dict['country'] = int(year), country

        actors = self._strip_attr(
            self._extract_item(result, 'Darsteller')
        )
        if actors:
            actors = [(None, actor) for actor in self._strip_attr(actors.split(','))]

        result_dict['actors'] = actors

        # ugly, I know
        poster, _ = result.find(
            "div", {"class": "title_cover_image_box"}
        ).find("a").get("href").split('?', 1)
        if poster:
            result_dict['poster'] = [(None, poster)]
        print(result_dict['poster'])
        result_dict['imdbid'] = "-"
        result_dict['genre_norm'] = "-"

        # to be done
        result_dict['rating'] = "-"

        return result_dict

    def _extract_item(self, response, tag):
        content = response.find(
            "div",{"class":"title_dtl_below_tab active_tab_details"}
        )
        for item in content.find_all("div", {"class":"txt"}):
            try:
                label = item.find("div", {"class":"label"})
                content = item.find("div", {"class":"content"})
                if label and content:
                    if tag.upper().strip() in label.get_text().upper().strip() :
                        return content.get_text()
            except AttributeError as e:
                print(e)

    def _strip_attr(self, attr):
        if isinstance(attr, list):
            return [s.strip() for s in attr]
        if isinstance(attr, str):
            return attr.strip()


    @property
    def supported_attrs(self):
        return self._attrs
