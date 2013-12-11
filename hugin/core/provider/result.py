#!/usr/bin/env python
# encoding: utf-8

""" Represens a finished result that hugin understands. """


class Result:
    """
    A Object representing a result.

    The movie result contains following parameters:

        * provider that was used
        * the provider filled in result_dict
        * number of retries used
        * result type, according to type in query params

    """

    def __init__(self, provider, query, result, retries):
        """
        A normalized result containing provider and job/result items.

        :param provider: The provider responsible for the result.
        :param result: The result dict the provider filled in.
        :param query: The query was used to generate the result dict.
        :param retries: The number of retries was used to get the job done.

        """
        self._provider = provider
        self._search_params = query
        self._result_type = self._search_params['type']
        self._retries = retries
        self._result_dict = result

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def get_provider(self, provider):
        self._provider = provider

    @property
    def result_dict(self):
        return self._result_dict

    def __repr__(self):
        result = self._result_dict is not None and self._result_dict != []
        return '{0} ==> {1}, Item found: {2}, Retries: {3}'.format(
            self._provider, self._result_type, result, self._retries
        )
