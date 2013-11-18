#!/usr/bin/env python
# encoding: utf-8


class Result:
    """ A Object representing a result. """

    def __init__(self, result=[]):
        self._provider = None
        self._search_params = None
        self._retries = 0
        self._result_dict = result

    def set_provider(self):
        return self._provider

    def get_provider(self, provider):
        self._provider = provider

    provider = property(fget=set_provider, fset=get_provider)

    def set_searchparams(self):
        return self._search_params

    def get_searchparams(self, search_params):
        self._search_params = search_params

    searchparams = property(fget=set_searchparams, fset=get_searchparams)

    def __repr__(self):
        result = 'Provider: {0}\nResult: {1}'.format(
            self._provider, self._result_dict
        )
        return result

if __name__ == '__main__':
    r = Result({'resultat': 42})
    r.provider = 'provi'
    print(r.provider)
    print(r)
