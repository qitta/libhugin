#!/usr/bin/env python
# encoding: utf-8

""" This module provides the Interface definition for provider, converter and
postprocessing plugins.

"""

from yapsy.IPlugin import IPlugin

__all__ = ['IMovieProvider', 'IPersonProvider', 'IPictureProvider',
           'IOutputConverter', 'IPostprocessing', 'IProvider']


class IProvider(IPlugin):

    """ Abstract provider base class for movie and person subclasses.

    All content providers have to implement the following two methods:

    .. autosummary::

        build_url
        parse_response

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

        :param list search_params: A dictionary containing query parameters
        :returns list: A list with urls on success, else None

        """
        raise NotImplementedError

    def parse_response(self, url_response, search_params):
        """
        Parse a previously requested http response.

        The provider itself is responsible for parsing its previously requested
        items.

        Possible result return values are:

            * list with urls to fetch next
            * a empty list if nothing found
            * a finished result_dict
            * None if parsing fails

        The method returns a  tuple containing a flag that indicates if
        provider is done. If the flag is True, than there is nothing to do
        left, otherwise the query is not ready yet.

        Possible combinations  ::

            * on valid response:     => ([[url_a, url_b, ...],...], False)
                                        ([], True)
                                        (result, True)
                                        (None, False)

            * on invalid response:   => (None, True)

        The (None, False) case is for provider that may get a valid response
        which tells that the database/server had a timeout. In this case just
        return (None, False) and a retry will be triggered.

        :param url_response: A url-response tuple list.
        :type url_response: list
        :param search_params: See :func: `core.provider.IProvider.search`.
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


#    """ a base class for movie metadata plugins.
#    .. py:function:: attribute_format
#
#        :param title: was ist der title
#        :type title: [str]

class IMovieProvider(IProvider):

    """ a base class for movie metadata plugins.

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
        :param list alternative_titles': Alternative titles list as (lang, title) tuple.
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

    pass


class IMoviePictureProvider(IProvider):
    pass


class IPersonProvider(IProvider):

    """ A base class for person metadata plugins.

    .. note:: The movie provider should fill the result dict according to the parameters listened below.

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
    pass


class IPersonPictureProvider(IProvider):
    pass


# converter plugins
class IOutputConverter(IPlugin):

    """ A base class for output converter plugins.  """
    def __init__(self):
        self.name = 'IOutputConverter name placeholder'
        self.description = 'IOutputConverter description placeholder'

    def __repr__(self):
        return '{name} <{description}>'.format(
            name=self.name, description=self.description
        )


#  postprocessing plugins
class IPostprocessing(IPlugin):

    """ A base class postprocessing plugins.  """
    def __init__(self):
        self.name = 'IOutputConverter name placeholder'
        self.description = 'IOutputConverter description placeholder'

    def __repr__(self):
        return '{name} <{description}>'.format(
            name=self.name, description=self.description
        )
