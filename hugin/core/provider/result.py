#!/usr/bin/env python
# encoding: utf-8


class Result:
    """ A Object representing a result. """

    def __init__(self, result=[]):
        self._provider = None
        self._search_params = None
        self.retries = None
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
        if self._search_params['type'] == 'person':
            return self._repr_person()
        else:
            return self._repr_movie()

    def _repr_person(self):
        if self._result_dict is not None and self._result_dict != []:
            result = 'provider: {0}\nresult: {1}\nname: {2}\nRetries: {3}'.format(
                self._provider, 'complete.', self._result_dict['name'],
                self.retries
            )
        else:
            result = 'provider: {0}\nresult: {1}\nname: {2}\nRetries: {3}'.format(
                self._provider, self._result_dict, '', self.retries
            )
        return result

    def _repr_movie(self):
        if self._result_dict is not None and self._result_dict != []:
            result = 'provider: {0}\nresult: {1}\ntitel: {2}\nRetries: {3}'.format(
                self._provider, 'complete.', self._result_dict['title'],
                self.retries
            )
        else:
            result = 'provider: {0}\nresult: {1}\ntitel:{2}\nRetries: {3}'.format(
                self._provider, self._result_dict, '', self.retries
            )
        return result

if __name__ == '__main__':
    r = Result({'resultat': 42})
    r.provider = 'provi'
    print(r.provider)
    print(r)
