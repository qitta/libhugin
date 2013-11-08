#!/usr/bin/env python
# encoding: utf-8

""" Caching valid http responses. """


from threading import Lock
import shelve
import os


class Cache(object):

    """ Http response cache. """

    def __init__(self):
        self._cache = None
        self._cache_lock = Lock()

    def open(self, path='.', cache_name='shelve_cache.db'):
        """ Open a new cache or read existing cache, if cache exists. """
        if self._cache is None:
            full_path = os.path.join(path, cache_name)
            if not os.path.exists(path):
                os.mkdir(path)
            self._cache = shelve.open(full_path)

    def read(self, key):
        """ Read data from cache at position of key."""
        with self._cache_lock:
            if self._cache is None:
                print('Error, no open cache. - read')
            else:
                return self._cache.get(key)

    def write(self, key, value):
        with self._cache_lock:
            """ Write value at key position, overwrite existing items. """
            if self._cache is None:
                print('Error, no open cache. - write')
            else:
                self._cache[key] = value

    def get_cache_object(self):
        return self._cache

    def close(self):
        """ Sync and close the open cache. """
        if self._cache is None:
            print('Error, no open cache.')
        else:
            self._cache.sync()
            self._cache.close()
            self._cache = None

if __name__ == '__main__':
    c = Cache()
    c.open()
    c.open()
    c.write('3', 4908)
    c.write('5', 47821)
    print(c.read('5'))
    print(c.read('3'))
    c.close()
