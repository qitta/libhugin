#!/usr/bin/env python
# encoding: utf-8

""" This module provides the Interface definition for provider, converter and
postprocessor plugins.
"""

from yapsy.IPlugin import IPlugin

__all__ = ['IMovieProvider', 'IPersonProvider', 'IPictureProvider',
           'IConverter', 'IPostprocessor', 'IProvider']

MOVIE_ATTR_MASK = [
    'title', 'original_title', 'plot', 'runtime', 'imdbid', 'vote_count',
    'rating', 'providerid', 'alternative_titles', 'directors', 'writers',
    'crew', 'year', 'poster', 'fanart', 'countries', 'genre', 'genre_norm',
    'collection', 'studios', 'trailers', 'actors', 'keywords', 'tagline',
    'outline'
]

PERSON_ATTR_MASK = [
    'name', 'alternative_names', 'photo', 'birthday', 'placeofbirth',
    'imdbid', 'providerid', 'homepage', 'deathday', 'popularity',
    'biography', 'known_for'
]


def movie_result_mask(result):
    return _result_mask(result, MOVIE_ATTR_MASK)


def person_result_mask(result):
    return _result_mask(result, PERSON_ATTR_MASK)


def _result_mask(result, mask):
    result_mask = {key: None for key in mask}
    if result:
        result_mask.update(result)
    return result_mask


class IProvider(IPlugin):

    """ Abstract provider base class for movie and person subclasses.

    All content providers have to implement the following two methods:

    """
    def __init__(self):
        self.name = 'IProvider'
        self.description = 'IProvider description'

    def build_url(self, search_params):
        """
        Build a url from given search params.

        The build_url method builds a url according to the given search
        parameters.  The build_url method has to return a list with URIs or
        None if building a search URIs fails.

        :param dict search_params: A dictionary containing query parameters. \
        For more information about search possible search parameters see \
        :meth:`hugin.harvest.session.Session.create_query`.

        :returns list list: A list with urls on success, else None

        """
        raise NotImplementedError

    def parse_response(self, url_response, search_params):
        """
        Parse a previously requested http response.

        The provider itself is responsible for parsing its previously requested
        items.

        The method returns a *tuple* containing a *result* and a *flag* that
        indicates if provider is done. If the flag is True, than there is
        nothing to do left, otherwise the query is not ready yet.


        The following return values, *tuple combinations* are possible:

        **on valid http response:**

        +----------------------------------------+-------+
        | result                                 | flag  |
        +========================================+=======+
        | A list with url lists:                 |       |
        | [[url_a, url_b,...],...])              | False |
        +----------------------------------------+-------+
        | A empty list: []                       | True  |
        +----------------------------------------+-------+
        | result_dict, with attributes formatted | True  |
        | accourding to :class:`IMovieProvider`  |       |
        | or :class:`IPersonProvider`            |       |
        +----------------------------------------+-------+
        | None                                   | False |
        +----------------------------------------+-------+

        The (None, False) case is for provider that may get a valid response
        which tells that the database/server had a timeout. In this case just
        return (None, False) and a retry will be triggered.


        **on invalid http response:**

        +----------------------------------------+-------+
        | result                                 | flag  |
        +========================================+=======+
        | None                                   | True  |
        +----------------------------------------+-------+

        :param list url_response: A url-response tuple list.

        This parameter is a list with tuples containing the url and the http
        response downloaded from this url source.

        :param dict search_params: Search parameters from query.

        This dict contains all the search paramesters from the query. Not all
        parameters might be relevant for the content provider. For a list with
        all possible query parameters see
        :meth:`hugin.harvest.session.Session.create_query`.

        :returns: A tuple containing a data and a state flag.

        """
        raise NotImplementedError

    @property
    def supported_attrs(self):
        """
        Get the attributes that are filled in by the provider.

        :returns: A list with result attributes supported by provider.

        """
        raise NotImplementedError

    def identify_type(self):
        types = self._types()
        maintype = 'movie' if 'movie' in types else 'person'
        if 'picture' in types:
            return '{maintype}_{subtype}'.format(
                maintype=maintype,
                subtype='picture'
            )
        return maintype

    def _types(self):
        provider_types = {
            'person': [IPersonProvider],
            'movie': [IMovieProvider],
            'picture': [IMoviePictureProvider, IPersonPictureProvider]
        }
        types = []
        for string, instances in provider_types.items():
            for instance in instances:
                if isinstance(self, instance):
                    types.append(string)
        return types

    def __repr__(self):
        types = ', '.join(self._types())
        return '{name} <{type}>'.format(name=self.name, type=types)


class IMovieProvider(IProvider):

    """ A base class for movie metadata plugins.

        .. note::

            The movie provider should fill the result dict according to the
            parameters listened below.

        :param str title': Movie title.
        :param str original_title': Original Movie title.
        :param str plot': Movie overview.
        :param int runtime': Runtime in minutes.
        :param str imdbid': A imdbid if available.
        :param int vote_count': A Vote count.
        :param str rating': A uer rating.
        :param str providerid': A Provider id.
        :param list alternative_titles': Alternative titles list.
        :param list directors': Movie directors.
        :param list writers': Movie writers.
        :param list crew': Movie crew as (position, name) tuple.
        :param int year': Release date of the movie.
        :param list poster': A Poster list as (size, url) tuple.
        :param list fanart': A Fanart list as (size, url) tuple.
        :param list countries': A list with production countries.
        :param list genre': A genre list.
        :param list genre_norm': A libhugin normalized genre list.
        :param list collection': A list with collections movie belongs to.
        :param list studios': A list with studios involved in movie production.
        :param list trailers': A list with tuples (size, trailer url).
        :param list actors': A actor list with tuples (rolename, name)
        :param list keywords': A list with movie keywords if available.
        :param str tagline': A tagline.
        :param str outline': A outline.

    """
    def __init__(self):
        self._keys = MOVIE_ATTR_MASK
        raise NotImplementedError


class IMoviePictureProvider(IProvider):
    pass


class IPersonProvider(IProvider):

    """ A base class for person metadata plugins.

    .. note::

        The person provider should fill the result dict according to the
        parameters listened below.

    :param str name': Actor's name.
    :param list alternative_names': Alternative actor names like 'artist name'.
    :param list photo': A list with (size, photo url) tuples.
    :param str birthday': A birthday date.
    :param str placeofbirth': Place of birth.
    :param str imdbid': The actors imdbid if available.
    :param str providerid': The actors provider id.
    :param list homepage': A list with actor homepages.
    :param str deathday': A deathday date.
    :param str popularity': A popularity indicator.
    :param str biography': A actor biography.
    :param list known_for': Movies actor is know for.

    """
    def __init__(self):
        self._keys = PERSON_ATTR_MASK
        raise NotImplementedError


class IPersonPictureProvider(IProvider):
    pass


# converter plugins
class IConverter(IPlugin):

    """ A base class for output converter plugins.  """
    def __init__(self):
        self.name = 'IConverter name placeholder'
        self.description = 'IConverter description placeholder'

    def convert(self, result):
        """ Convert a single result object.

        :param result: A result object with a valid result_dict.
        :returns: A to the output coverter specified string repr of the result.

        """
        raise NotImplementedError

    def __repr__(self):
        return '{name} <{description}>'.format(
            name=self.name, description=self.description
        )

    def parameters(self):
        return {}


#  postprocessor plugins
class IPostprocessor(IPlugin):

    """ A base class postprocessor plugins.  """
    def __init__(self):
        self.name = 'IConverter name placeholder'
        self.description = 'IConverter description placeholder'

    def process(self, result):
        """ Convert a single result object.

        :param result: A result object with a valid result_dict.
        :returns: A to the output coverter specified string repr of the result.

        """
        raise NotImplementedError

    def __repr__(self):
        return '{name} <{description}>'.format(
            name=self.name, description=self.description
        )

    def parameters(self):
        return {}
