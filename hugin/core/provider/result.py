#!/usr/bin/env python
# encoding: utf-8


class Result:
    """ A Object representing a result. """

    def __init__(self, provider, query, result, retries):
        self._provider = provider
        self._search_params = query
        self._result_type = self._search_params['type']
        self._retries = retries
        self._result_dict = result

    def set_provider(self):
        return self._provider

    def get_provider(self, provider):
        self._provider = provider

    provider = property(fget=set_provider, fset=get_provider)

    def is_valid(self):
        return self._result_dict is not None and self._result_dict != []

    def __repr__(self):
        result = self._result_dict is not None and self._result_dict != []
        return '{0} ==> {1}, Item found: {2}, Retries: {3}'.format(
            self._provider, self._result_type, result, self._retries
        )
