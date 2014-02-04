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
            'title', 'plot', 'directors', 'actors', 'year', 'genre',
            'keywords', 'countries', 'studios', 'original_title', 'poster',
            'tagline'
        }

    def build_url(self, search_params):
        if search_params.title:
            return [self._base_url.format(
                quote_plus(search_params.title, encoding='latin-1')
            )]

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
            for item in result.find_all("div", {"class": "name"}):
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
    def _parse_tagline(self, response):
        tagline_tag = response.find("p", {"class":"long_name"})
        if tagline_tag:
            return self._strip_attr(tagline_tag.get_text())

    def _parse_movie_module(self, result, search_params):
        result_dict = {k: None for k in self._attrs}

        result_dict['title'] = self._parse_title(result)
        result_dict['tagline'] = self._parse_tagline(result)
        result_dict['original_title'] = self._parse_attribute(
            result, 'Originaltitel'
        )
        result_dict['plot'] = self._parse_plot(result)

        countries, year = self._parse_countries_year(result)
        result_dict['countries'], result_dict['year'] = countries, year

        result_dict['actors'] = self._parse_actors(result)
        result_dict['poster'] = self._parse_poster(result)

        result_dict['directors'] = self._parse_attribute(result, 'regie')
        result_dict['genre'] = self._parse_attribute(result, 'genre')
        result_dict['keywords'] = self._parse_attribute(result, 'Schlagwört')
        result_dict['studios'] = self._parse_attribute(result, 'Studio')

        return result_dict

    def _parse_title(self, response):
        title = self._strip_attr(
            response.find("h1", {"class": "name"}).get_text()
        )
        return self._strip_attr(title)

    def _parse_plot(self, response):
        plot = response.find(
            "div", {"class": "txt movie_description"}
        ).get_text()

        # last paragraph of plot dosen't belong to the paragraph, so we want to
        # split it and throw it away
        plot, *_ = plot.rsplit('\r', maxsplit=1)
        return self._strip_attr(plot)

    def _parse_countries_year(self, response):
        country_year_tag = self._extract_tag(response, 'produktion')
        if country_year_tag:
            countries, year = country_year_tag.rsplit(maxsplit=1)
            if year.isnumeric():
                return self._strip_attr(countries.split(',')), int(year)
            return self._strip_attr(countries.split(',')), None

    def _parse_actors(self, response):
        actors = self._extract_tag(response, 'Darsteller')
        if actors:
            actors = [(None, actor) for actor in self._strip_attr(
                actors.split(',')
            )]
            return actors

    def _parse_poster(self, response):
        postertag = response.find(
            "div", {"class": "title_cover_image_box"}
        ).find("a").get("href")
        if postertag:
            poster = postertag.split('?', 1)
            return [(None, poster)]

    def _parse_attribute(self, response, attr):
        attr_list = self._extract_tag(response, attr)
        if attr_list:
            if 'Original' in attr:
                return self._strip_attr(attr_list)
            else:
                return self._strip_attr(attr_list.split(','))

    def _extract_tag(self, response, tag):
        content = response.find(
            "div", {"class": "title_dtl_below_tab active_tab_details"}
        )
        for item in content.find_all("div", {"class": "txt"}):
            try:
                label = item.find("div", {"class": "label"})
                content = item.find("div", {"class": "content"})
                if label and content:
                    if tag.upper().strip() in label.get_text().upper().strip():
                        return content.get_text()
            except AttributeError as e:
                print('AttributeError in _extract_tag videobuster:', e)

    def _strip_attr(self, attr):
        if isinstance(attr, list):
            return [s.strip() for s in attr]
        if isinstance(attr, str):
            return attr.strip()

    @property
    def supported_attrs(self):
        return self._attrs
