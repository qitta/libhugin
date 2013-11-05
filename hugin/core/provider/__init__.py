#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin
import abc

__all__ = ['IMovieProvider', 'IPersonProvider', 'IPictureProvider',
           'IOutputConverter', 'IPostprocessing', 'IProvider']


class IProvider(IPlugin):
    """
    This abstract interface declares methods to be implemented by all provider
    plugins.
    """

    def search(self, search_params):
        """
        The search method builds the url according to the given search
        parameters.  The search method has to return a tuple containing data
        and a flag. Data might be the url string on success or None if building
        the url fails.

        :param search_params: A dictionary containing query parameters
        :returns: A url on success, else None

        """

        raise NotImplementedError

    def parse(self, response, search_params):
        """
        The provider itself is responsible for parsing its previously requested
        data.  Data might be a list of new urls to fetch, a empty list or a
        finished result object.

        The state flag indicates if provider is done. If the flag is True,
        than there is nothing to do left, otherwise the query is not ready yet.

        Possible combinations ::

            valid response      =>  ([url,...], False)
                                    (None, False)
                                    ([], True)
                                    (result, True)

            invalid response    => (None, True)

        :param response: A utf-8 encoded http response.
        :type response: str
        :param search_params: See :func: `core.provider.IProvider.search`.
        :returns: A tuple containing a data and a state flag.


        """

        raise NotImplementedError

    @property
    def supported_attrs(self):
        '''
        Helper function to determinate which result attribues are handled by
        the provider.

        :returns: A list with result attributes supported by provider.
        '''
        return []

    def set_name(self, name):
        setattr(self, '_name', name)

    def get_name(self):
        return self._name

    name = property(fget=get_name, fset=set_name)

    @property
    def is_picture_provider(self):
        return isinstance(self, IPictureProvider)

    @property
    def is_movie_provider(self):
        return isinstance(self, IMovieProvider)

    @property
    def is_person_provider(self):
        return isinstance(self, IPersonProvider)

    def __repr__(self):
        return '{name} <{type}>'.format(name=self._name, type=self._type)

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
        return ', '.join(types)


class IMovieProvider(IProvider):
    """
    A base class for movie metadata plugins. All metadata plugins should
    inherit from this class.
    """

    pass


class IPersonProvider(IProvider):
    """
    A base class for person metadata plugins. All person metadata plugins
    should inherit from this class.
    """
    pass


class IPictureProvider(IProvider):
    @property
    def is_picture(self):
        return True


# converter plugins
class IOutputConverter(IPlugin):
    """
    A base class for output converter plugins. All output converter should
    inherit from this class.
    """
    pass


#  postprocessing plugins
class IPostprocessing(IPlugin):
    """
    A base class postprocessing plugins. All postprocessing plugins should
    inherit from this class.
    """
    pass
