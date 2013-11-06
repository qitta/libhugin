#/usr/bin/env python
# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor
from http.client import BadStatusLine
from queue import Queue, Empty
from functools import partial
from threading import Lock
from hugin.common.utils import logutil
import logging
import socket
import urllib.request
import charade
import httplib2

USER_AGENT = None
LOGGER = logging.getLogger('hugin.downloader')


class DownloadQueue:

    def __init__(self, num_threads=25, user_agent=USER_AGENT, timeout_sec=5):
        '''
        A simple multithreaded queue wrapper for simultanous downloading using
        standard queue and futures ThreadPoolExecutor. Provider data
        dictionaries can only be used.

        :param num_threads: Number of threads to be used for simultanous
        downloading
        :param user_agent: User-Agent to be used.
        :param timeout: Url timeout to be used for each url
        '''
        self._url_to_provider_data_lock = Lock()
        self._executor = ThreadPoolExecutor(max_workers=num_threads)
        self._headers = {'User-Agent': user_agent}
        self._request_queue = Queue()
        self._url_to_provider_data = {}
        self._timeout_sec = timeout_sec

    def _fetch_url(self, url, timeout):
        """
        Download method which is triggered by ThreadPoolExecutor for
        downloading.

        :param url: Url to be downloaded
        :param timeout: Timeout in seconds

        :returns: Request code and request itself as tuple => (r code, r)
        """
        http = httplib2.Http(timeout=timeout)
        resp, content = http.request(url)
        return (resp.status, content)
        #with urllib.request.urlopen(url, timeout=timeout) as request:
        #    return (request.code, request.readall())

    def _future_callback(self, url, future):
        """
        Callback that is triggered by a future on sucess or error.

        :param url: The url is used to pop finished/failed provider data
        elements from url_to_provider_data dictionary and put them into result
        queue
        """
        with self._url_to_provider_data_lock:
            provider_data = self._url_to_provider_data.pop(url)
            try:
                return_code, result = future.result()
                if result and return_code:
                    provider_data['response'] = self._encode_to_utf8(result)
                    provider_data['return_code'] = return_code
            except (
                ValueError,
                socket.timeout,
                urllib.error.URLError,
                BadStatusLine
            ) as e:
                provider_data['return_code'] = 408
                LOGGER.warning('timeout')
            self._request_queue.put(provider_data)

    def _encode_to_utf8(self, byte_data):
        """
        Tries to decode bytestream to utf-8. If this fails, encoding is guessed
        by charade and decoding is repeated with just dedected encoding.

        :param byte_data: A bytestream that will be ecoded to its specific
        encoding characteristics

        :returns: Decoded byte_data
        """
        try:
            return byte_data.decode('utf-8')
        except (TypeError) as e:
            print(e, 'trying to use charade now to quess encoding.')
            encoding = charade.detect(byte_data).get('encoding')
            return byte_data.decode(encoding)

    def push(self, provider_data):
        '''
        Feeds DownloadQueue with provider_data dictionary. The url to fetch is
        used as key for url_to_provider_data dictionary. Provider_data with
        urls that are already being processed, will be ignored.

        :param provider_data: A dictionary that encapsulates some provider
        information url, response, provider.
        '''
        url = provider_data['url']
        if url and url not in self._url_to_provider_data:
            with self._url_to_provider_data_lock:
                self._url_to_provider_data[url] = provider_data
            self._executor.submit(
                self._fetch_url,
                url=url,
                timeout=self._timeout_sec).add_done_callback(
                    partial(self._future_callback, url)
                )

    def running_jobs(self):
        print(len(self._url_to_provider_data), self._request_queue.qsize())

    def pop(self):
        '''
        Simple DownloadQueue get wrapper

        :returns: Next avaiable provider data object.
        :raises:  Empty exception if queue is empty.
        '''
        try:
            return self._request_queue.get_nowait()
        except Empty:
            if len(self._url_to_provider_data) == 0:
                raise Empty
            else:
                return self._request_queue.get()


if __name__ == '__main__':
    import unittest
    import json

    class TestDownloadQueue(unittest.TestCase):

        def setUp(self):
            self._dq = DownloadQueue(timeout_sec=2)
            self._urls = ['http://www.nullcat.de', 'http://httpbin.org/get']
            logutil.create_logger(None)

        #def _create_dummy_provider(self, url):
        #    pd = create_provider_data(
        #        provider='',
        #        retries=5
        #    )
        #    pd['url'] = url
        #    return pd

        #def test_push_pop(self):
        #    with open('hugin/core/testdata/imdbid_small.txt', 'r') as f:
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
        #            print(e)
        #        except Exception as E:
        #            print(E)

    unittest.main()
