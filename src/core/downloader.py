#/usr/bin/env python
# encoding: utf-8

from requests.exceptions import Timeout, InvalidSchema, ConnectionError
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Lock
from queue import Queue, Empty
import urllib.request
import requests


USER_AGENT = "libhugin 'rebellic raven'/0.1"


class DownloadQueue:
    def __init__(self, num_threads=50, user_agent=USER_AGENT, timeout=1):
        '''
        A simple multithreaded add/get download queue wrapper using standard
        queue and future-requests

        :param num_threads: Number of threads to be used for simultanous
                            downloading
        '''
        self._url_to_provider_data_lock = Lock()
        self._executor = ThreadPoolExecutor(max_workers=num_threads)
        self._headers = {'User-Agent': user_agent}
        self._request_queue = Queue()
        self._url_to_provider_data = {}
        self._timeout = timeout

    def _fetch_url(self, url, timeout):
        return requests.get(url, timeout=timeout, headers=self._headers)
        # return urllib.request.urlopen(url, timeout=timeout)

    def _future_callback(self, url, future):
        with self._url_to_provider_data_lock:
            provider_data = self._url_to_provider_data.pop(url)
            try:
                provider_data['response'] = future.result()
                provider_data['response'].close()
            except (Timeout, InvalidSchema, ConnectionError) as e:
                print(e)
                provider_data['retries'] -= 1
            self._request_queue.put(provider_data)

    def push(self, provider_data):
        '''
        Feeds DownloadQueue with url to fetch

        :param provider_data: A dictionary that encapsulates some provider
        information url, response, provider
        '''
        url = provider_data['url']
        if url and url not in self._url_to_provider_data:
            with self._url_to_provider_data_lock:
                self._url_to_provider_data[url] = provider_data
            self._executor.submit(
                self._fetch_url,
                url=url,
                timeout=self._timeout).add_done_callback(
                    partial(self._future_callback, url)
                )

    def pop(self):
        '''
        Simple DownloadQueue get wrapper

        :returns: Next avaiable response object.
        :raises:  Empty if queue is empty.
        '''
        try:
            return self._request_queue.get_nowait()
        except Empty:
            if not len(self._url_to_provider_data) > 0:
                raise
            else:
                return self._request_queue.get()


if __name__ == '__main__':
    import unittest
    import time
    from core.providerhandler import create_provider_data

    class TestDownloadQueue(unittest.TestCase):

        def setUp(self):
            self._dq = DownloadQueue()
            self._urls = ['http://www.nullcat.de', 'http://httpbin.org/get']

        def _create_dummy_provider(self, url):
            pd = create_provider_data(
                provider='',
                retries=5
            )
            pd['url'] = url
            return pd

        def test_push_pop(self):
            f = open('core/tmp/imdbid_small.txt', 'r').read().splitlines()
            for item in f:
                url = 'http://www.omdbapi.com/?i={imdbid}'.format(imdbid=item)
                p = self._create_dummy_provider(url)
                self._dq.push(p)

            for item in f:
                print(self._dq.pop())

            for url in self._urls:
                pd = self._create_dummy_provider(url)
                pd = self._dq.push(pd)
                pd = self._dq.pop()
                self.assertTrue(pd is not None)
                self.assertTrue(pd['response'] is not None)

        def test_pop_from_empty(self):
            # pull from empty queue, Empty Exception will be raised
            with self.assertRaises(Empty):
                self._dq.pop()

    unittest.main()
