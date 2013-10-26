#/usr/bin/env python
# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor
from http.client import BadStatusLine
from queue import Queue, Empty
from functools import partial
from threading import Lock
from common.utils import logutil
import logging
import contextlib
import socket
import urllib.request
import charade


USER_AGENT = "libhugin 'rebellic raven'/0.1"
LOGGER = logging.getLogger('hugin.downloader')

class DownloadQueue:
    def __init__(self, num_threads=10, user_agent=USER_AGENT, timeout=5):
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
        headers = {'connection': 'close'}
       # with urllib.request.Request(url, headers=headers) as request:
        with urllib.request.urlopen(url, timeout=timeout) as request:
            return (request.code, request.readall())

    def _future_callback(self, url, future):
        with self._url_to_provider_data_lock:
            provider_data = self._url_to_provider_data.pop(url)
            try:
                _, result = future.result()
                if result:
                    provider_data['response'] = self._encode_to_utf8(result)
            except (
                ValueError,
                socket.timeout,
                urllib.error.URLError,
                BadStatusLine
            ) as e:
                LOGGER.warning('Timeout')
            self._request_queue.put(provider_data)

    def _encode_to_utf8(self, data):
        try:
            return data.decode('utf-8')
        except (TypeError) as e:
            print(e, 'trying to use charade now to quess encoding.')
            encoding = charade.detect(data).get('encoding')
            return data.decode(encoding)

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
            return self._request_queue.get()
        except Empty:
            if not len(self._url_to_provider_data) > 0:
                raise
            else:
                return self._request_queue.get()


if __name__ == '__main__':
    import unittest
    import time
    import json
    from core.providerhandler import create_provider_data

    class TestDownloadQueue(unittest.TestCase):

        def setUp(self):
            self._dq = DownloadQueue(timeout=2)
            self._urls = ['http://www.nullcat.de', 'http://httpbin.org/get']
            logutil.create_logger(None)

        def _create_dummy_provider(self, url):
            pd = create_provider_data(
                provider='',
                retries=5
            )
            pd['url'] = url
            return pd

        #def test_push_pop(self):
        #    with open('core/testdata/imdbid_huge.txt', 'r') as f:
        #        imdbid_list = f.read().splitlines()
        #    for item in imdbid_list:
        #        #url = 'http://www.omdbapi.com/?i={imdbid}'.format(imdbid=item)
        #        url = 'http://ofdbgw.org/imdb2ofdb_json/{0}'.format(item)
        #        p = self._create_dummy_provider(url)
        #        self._dq.push(p)

        #    while True:
        #        rpd = self._dq.pop()
        #        res = rpd['response']
        #        try:
        #            j = json.loads(res)
        #            rcode = j["ofdbgw"]["status"]["rcode"]
        #            if rcode == 2 and rpd['retries'] >= 0:
        #                p = self._create_dummy_provider(rpd['url'])
        #                p['retries'] -= 1
        #                self._dq.push(p)
        #            else:
        #                print(rpd['retries'], j['ofdbgw']['resultat']['titel'])
        #        except (TypeError, KeyError) as e:
        #            pass
        #        except Exception as E:
        #            pass

    unittest.main()
