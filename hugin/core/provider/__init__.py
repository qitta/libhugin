#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin


__all__ = ['IMovieProvider', 'IPersonProvider', 'IPictureProvider',
           'IOutputConverter', 'IPostprocessing', 'IProvider']


class IProvider(IPlugin):
    """
    This abstract interface declares methods to be implemented by all provider
    plugins.
    """

    @property
    def supported_attrs(self):
        return []

    def set_name(self, name):
        setattr(self, '_name', name)

    def get_name(self):
        return self._name

    name = property(fget=get_name, fset=set_name)

    def search(self, search_params):
        """
        :param search_params: A dictionary containing query parameters and
        the number of items to fetch. Query parameters are title, year and
        imdbid, if all parameters are available, imdbid will be prefered if
        possible.
        :returns: A tuple containing data and a 'finished' flag that can be

        Possible combinations ::

            valid search_params             => ([url,...], False)
            invalid search_params           => (None, True)
        """

        raise NotImplementedError

    def parse(self, response, search_params):
        """
        :param response: A utf-8 encoded http response. The provider itself is
        responsible for parsing its previously requested data.
        :param search_params: See :func: `core.provider.IProvider.search`.
        :returns: A tuple with data and a finished flag. Data may be a list of
        new urls to fetch, empty list or a finished result object. If the
        response is invalid, (None, False) will be returned. This triggers the
        retry mechanism. See :func: `core.provider.IProvider.search`. If the
        response is valid but parsing it fails, ([], True) is returned. Query
        is finished.

        Possible combinations ::

            valid response      =>  ([url,...], False)
                                    ([], True)
                                    (result, True)

            invalid response    => (None, False)
        """

        raise NotImplementedError

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
            'picture': IPersonProvider
        }
        types = []
        for string, instance in provider_types.items():
            if isinstance(self, instance):
                types.append(string)
        return ', '.join(types)



    def init(self):
        '''
        Initialisation of a provider
        :returns: True on success, else False
        '''
        return True




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
