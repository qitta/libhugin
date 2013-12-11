#!/usr/bin/env python
# encoding: utf-8

""" Interface definition for provider, converter and postprocessing plugins."""

from yapsy.IPlugin import IPlugin

__all__ = ['IMovieProvider', 'IPersonProvider', 'IPictureProvider',
           'IOutputConverter', 'IPostprocessing', 'IProvider']


class IProvider(IPlugin):

    """ This abstract interface to be implemented by all provider plugins.

    .. autosummary::

        build_url
        parse_response

    """
    def __init__(self):
        self.name = 'IProvider'

    def build_url(self, search_params):
        """
        Build a url out of given search params, entry point of all providers.


        The build url method builds a url according to the given search
        parameters.  The build_url method has to return a list with URIs or
        None if building a search URIs fails.

        :param search_params: A dictionary containing query parameters
        :returns: A list with urls on success, else None

        """
        raise NotImplementedError

    def parse_response(self, url_response, search_params):
        """
        Parse a url-http_response list with tuples.

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


class IMovieProvider(IProvider):

    """ A base class for movie metadata plugins.
<F3>
    .. py:function:: attribute_format

        :param title: Was ist der title
        :type title: [str]

    """

    # movie attrs to be documented
    #
    #'title': str,
    #'original_title': str,
    #'plot': str,
    #'runtime': int,
    #'imdbid': str,
    #'vote_count': int,
    #'rating': str,
    #'providerid': str,
    #'alternative_titles': list,
    #'directors': list,
    #'writers': list,
    #'crew': list,
    #'year': int,
    #'poster': list,
    #'fanart': list,
    #'countries': list,
    #'genre': list,
    #'genre_norm': list,
    #'collection': list,
    #'studios': list,
    #'trailers': list,
    #'actors': list,
    #'keywords': list,
    #'tagline': str,
    #'outline': str
    pass


class IMoviePictureProvider(IProvider):
    pass


class IPersonProvider(IProvider):

    """ A base class for person metadata plugins. """

    # person attrs to be documented
    #
    #'name': str,
    #'alternative_names': list,
    #'photo': list,
    #'birthday': str,
    #'placeofbirth': str,
    #'imdbid': str,
    #'providerid': str,
    #'homepage': list,
    #'deathday': str,
    #'popularity': str,
    #'biography': str,
    #'known_for': list
    pass


class IPersonPictureProvider(IProvider):
    pass


# converter plugins
class IOutputConverter(IPlugin):

    """ A base class for output converter plugins.  """

    pass


#  postprocessing plugins
class IPostprocessing(IPlugin):

    """ A base class postprocessing plugins.  """

    pass
