#!/usr/bin/env python
# encoding: utf-8

""" Interface definition for provider, converter and postprocessing plugins."""

from yapsy.IPlugin import IPlugin

__all__ = ['IMovieProvider', 'IPersonProvider', 'IPictureProvider',
           'IOutputConverter', 'IPostprocessing', 'IProvider']


class IProvider(IPlugin):

    """ This abstract interface to be implemented by all provider plugins. """

    def build_url(self, search_params):
        """
        Build a url out of given search params, entry point of all providers.


        The build url method builds a url according to the given search
        parameters.  The build_url method has to return a URI or None if
        building a search URI fails.

        :param search_params: A dictionary containing query parameters
        :returns: A url on success, else None

        """
        raise NotImplementedError

    def parse_response(self, response, search_params):
        """
        Parse a response http response.

        The provider itself is responsible for parsing its previously requested
        data via the build_url function.  Data might be a list of new urls to
        fetch, a empty list, a finished result object or None if parsing fails.

        The method returns a  tuple containing a flag that indicates if provider
        is done. If the flag is True, than there is nothing to do left,
        otherwise the query is not ready yet.

        Possible combinations ::

            valid response      =>  ([url,...], False)
                                    (None, False)
                                    ([], True)
                                    (result, True)

            invalid response    => (None, True)

        The (None, False) case is for provider that may get a valid response
        which tells that the database/server had a timeout. In this case just
        return (None, False) and a retry will be triggered.

        :param response: A utf-8 encoded http response.
        :type response: str
        :param search_params: See :func: `core.provider.IProvider.search`.
        :returns: A tuple containing a data and a state flag.

        """
        raise NotImplementedError

    def set_name(self, name):
        setattr(self, '_name', name)

    def get_name(self):
        return self._name

    name = property(fget=get_name, fset=set_name)

    @property
    def supported_attrs(self):
        """
        Get the attributes that are filled in by the provider.

        :returns: A list with result attributes supported by provider.

        """
        raise NotImplementedError

    @property
    def is_picture_provider(self):
        return isinstance(self, IPictureProvider)

    @property
    def is_movie_provider(self):
        return isinstance(self, IMovieProvider)

    def identify_type(self):
        types = self._type
        maintype = 'movie' if 'movie' in types else 'person'
        if 'picture' in types:
            return '{maintype}_{subtype}'.format(
                maintype=maintype,
                subtype='picture'
            )
        else:
            return '{maintype}'.format(maintype=maintype)

    @property
    def is_person_provider(self):
        return isinstance(self, IPersonProvider)

    @property
    def _type(self):
        provider_types = {
            'person': IPersonProvider,
            'movie': IMovieProvider,
            'picture': IPictureProvider
        }
        types = []
        for string, instance in provider_types.items():
            if isinstance(self, instance):
                types.append(string)
        return types

    def __repr__(self):
        types = ', '.join(self._type)
        return '{name} <{type}>'.format(name=self._name, type=types)


class IMovieProvider(IProvider):

    """ A base class for movie metadata plugins. """

    pass


class IPersonProvider(IProvider):

    """ A base class for person metadata plugins. """

    pass


class IPictureProvider(IProvider):

    """ A base class for picture metadata plugins.  """

    pass


# converter plugins
class IOutputConverter(IPlugin):

    """ A base class for output converter plugins.  """

    pass


#  postprocessing plugins
class IPostprocessing(IPlugin):

    """ A base class postprocessing plugins.  """

    pass
