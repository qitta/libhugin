#!/usr/bin/env python
# encoding: utf-8


from yapsy.IPlugin import IPlugin

__all__ = ['IMovieProvider', 'IPosterProvider', 'IBackdropProvider',
           'IPlotProvider', 'IPersonProvider', 'IOutputConverter',
           'IPostprocessing', 'IProvider']


class IProvider(IPlugin):
    """
    This abstract interface declares methods to be implemented by all provider
    plugins.
    """

    def search(self, search_params):
        """
        :params search_params: A dictionary containing query parameters and
        the number of items to fetch. Query parameters are title, year and
        imdbid, if all parameters are available, imdbid will be prefered if
        possible.

        :returns: A tuple containing data and a 'finished' flag that can be
        True or False. True indicates that the query is finished, False that
        there is data left to be processed.  If data is None, a retry will be
        triggered inside the core module, decrementing the num of retries
        inside the provider_data dictionary on every retry down to zero.

        Possible combinations ::

                valid response, item found      => ([url], False)
                valid response, nothing found   => ([], True)
                invalid response                => (None, False)
        """
        raise NotImplementedError

    def parse(self, response, search_params):

        """
        :params response: A utf-8 encoded http response. The provider itself is
        responsible for parsing its previously requested data.

        :params search_params: See :func `core.provider.IProvider.search`.

        :returns: A tuple with data and a finished flag. Data may be a list of
        new urls to fetch, empty list or a finished result object. If the
        response is invalid, (None, False) will be returned. This triggers the
        retry mechanism. See :func `core.provider.IProvider.search`. If the
        response is valid but parsing it fails, ([], True) is returned. Qeury
        is finiished.

        Possible combinations ::

                valid response      =>  ([url,...], False) or
                                        ([], True) or
                                        (result, True)

                invalid response    => (None, False)
                                       ([], True)
        """
        raise NotImplementedError


class IMovieProvider(IProvider):
    """
    Base class for movie metadata plugins. All metadata plugins shoud inherit
    from this class.
    """
    pass


class IPosterProvider(IProvider):
    """
    A base class for movie poster metadata plugins. All movie poster metadata
    plugins should inherit from this class.
    """
    pass


class IBackdropProvider(IProvider):
    """
    A base class for movie backdrop metadata plugins. All movie backdrop metadata
    plugins should inherit from this class.
    """
    pass


class IPhotoProvider(IProvider):
    """
    A base class for person photo metadata plugins. All person photo metadata
    plugins should inherit from this class.
    """
    pass


class IPersonProvider(IProvider):
    """
    A base class for person metadata plugins. All person metadata plugins shoud
    inherit from this class.
    """
    pass


# converter plugins

class IOutputConverter(IPlugin):
    pass


#  postprocessing plugins

class IPostprocessing(IPlugin):
    pass
