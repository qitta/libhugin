#!/usr/bin/env python
# encoding: utf-8

""" A simple caching implementation for http requests. """

from threading import Lock
import shelve
import os


class Cache:
    """
    Http response cache with a dict key value behavior.

    .. note::

        public methods:
            open(path, cache_name)
            read(key)
            write(key, value)
            close()

    """
    def __init__(self):
        self._cache = None
        self._cache_lock = Lock()

    def open(self, path='.', cache_name='shelve_cache.db'):
        """ Open a new cache or read existing cache, if cache exists.

        :param path: Path where cache should be saved.
        :param cache_name: Name of the cache to write/read from.

        """
        if self._cache is None:
            full_path = os.path.join(path, cache_name)
            if not os.path.exists(path):
                os.mkdir(path)
            self._cache = shelve.open(full_path)
            print('cache opened.')

    def read(self, key):
        """ Read data from cache at position of key.

        :param key: Key for value you want to lookup.

        """
        with self._cache_lock:
            if self._cache is None:
                print('Read error, no open cache.')
            else:
                return self._cache.get(key)

    def write(self, key, value):
        with self._cache_lock:
            """ Write value at key position, overwrite existing items.

            :param key: See :func: `read`.
            :param value: Value to be saved.

            """
            if self._cache is None:
                print('Write error, no open cache.')
            else:
                self._cache[key] = value

    def close(self):
        """ Sync all data and close the cache. """
        if self._cache is None:
            print('Close error, no open cache.')
        else:
            self._cache.sync()
            self._cache.close()
            print('cache closed.')
            self._cache = None

if __name__ == '__main__':
    import unittest

    class TestCache(unittest.TestCase):

        def setUp(self):
            self._cache = Cache()
            self._cache.open()

        def test_open_read(self):
            result = self._cache.read('there_is_no_such_key')
            self.assertTrue(result is None)

        def test_read_write(self):
            self._cache.write('key1', 'value1')
            self._cache.write('key2', 'value2')
            result = self._cache.read('key1')
            result2 = self._cache.read('key2')
            self.assertTrue(result == 'value1')
            self.assertTrue(result2 == 'value2')

        def test_write_close_read(self):
            self._cache.write('key3', 'value3')
            self._cache.close()
            self._cache.open()
            result = self._cache.read('key3')
            self.assertTrue(result == 'value3')

        def test_update_value(self):
            self._cache.write('key3', 'value3')
            result = self._cache.read('key3')
            self.assertTrue(result == 'value3')
            self._cache.write('key3', 'this_is_a_updated_value')
            self._cache.close()

            # lets open cache and read the previously updated value
            self._cache.open()
            result = self._cache.read('key3')
            self.assertTrue(result == 'this_is_a_updated_value')

        def tearDown(self):
            self._cache.close()

    unittest.main()
