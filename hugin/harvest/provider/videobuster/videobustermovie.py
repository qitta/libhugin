#!/usr/bin/env python
# encoding: utf-8

# stdlib
import re
from parse import parse
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
        self._movie_url = 'https://www.videobuster.de{}'
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
                    url = item.find("a").get("href")
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
        result_dict['title'] = self._extract_item(result, 'Originaltitel') or ''
        result_dict['plot'] = result.find(
            "div", {"class":"txt movie_description movie_description_short"}
        ).get_text().strip()
        result_dict['original_title'] = result_dict['title']
        result_dict['genre'] = self._extract_item(result, 'genre').replace('\n','').split(',')
        result_dict['directors'] = self._extract_item(result, 'regie').replace('\n','').split(',')
        country, year= self._extract_item(result, 'produktion').replace('\n','').rsplit(maxsplit=1)

        result_dict['year'] = int(year)
        result_dict['country'] = country

        ##to be done
        result_dict['poster'] = "-"
        result_dict['imdbid'] = "-"
        result_dict['rating'] = "-"
        result_dict['genre_norm'] = "-"

        return result_dict

    def _extract_item(self, response, tag):
        content = response.find(
            "div",{"class":"title_dtl_below_tab active_tab_overview"}
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

    @property
    def supported_attrs(self):
        return self._attrs
