#/usr/bin/env python
# encoding: utf-8

from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Lock
from queue import Queue, Empty
import requests


DEFAULT_USER_AGENT = "libhugin 'rebellic raven'/0.1"


class DownloadQueue:
    def __init__(self, num_threads=50, user_agent=DEFAULT_USER_AGENT):
        '''
        A simple multithreaded add/get download queue wrapper using standard
        queue and future-requests

        :param num_threads: Number of threads to be used for simultanous
                            downloading
        '''
        self._url_to_future_lock = Lock()
        self._session = FuturesSession(
            executor=ThreadPoolExecutor(max_workers=num_threads)
        )
        self._session.headers['User-Agent'] = user_agent
        self._request_queue = Queue()
        self.url_to_future = {}

    def push(self, url):
        '''
        Feeds DownloadQueue with url to fetch
        //TODO: Exchange url with ProviderDataObject

        :param url: Given url to be downloaded
        '''
        with self._url_to_future_lock:
            if url not in self.url_to_future:
                future = self._session.get(
                    url,
                    timeout=0.2,
                    background_callback=partial(
                        self._response_finished,
                        url=url
                    )
                )
                self.url_to_future[url] = future

    def pop(self):
        '''
        Simple DownloadQueue getter

        :returns: Next avaiable response object.
        :raises:  LookupError if queue is empty.
        '''
        try:
            return self._request_queue.get_nowait()
        except Empty:
            if len(self.url_to_future) > 0:
                return self._get_stalled_futures()
            else:
                raise LookupError('download queue is empty.')

    def _get_stalled_futures(self):
        '''
        Checks futures dictionary for stalled or timeouted futures.

        :returns: Future result, if a timeout occured, 'timeout' is returned.
        :raises:  LookupError if queue is empty and no futures are done.
        '''
        with self._url_to_future_lock:
            for url, future in self.url_to_future.items():
                if future.done() is True:
                    try:
                        return self.url_to_future.pop(url).result()
                    except requests.exceptions.Timeout:
                        return 'timeout while fetching:'.format(url)
                else:
                    raise LookupError('no url done yet.')

    def _response_finished(self, _, response, url):
        '''
        :param response: Finished response object
        :param url: Given url to download
        '''
        with self._url_to_future_lock:
            self.url_to_future.pop(url)
        self._request_queue.put(response)


# some testing purposes
if __name__ == '__main__':
    import time

    dq = DownloadQueue()
    imdbids = open('core/imdbid_small.txt', 'r').read().splitlines()

    for imdbid in imdbids:
        url = 'http://www.omdbapi.com/?i={0}'.format(imdbid)
        # url = 'http://httpbin.org/get'
        # url = 'http://ofdbgw.org/imdb2ofdb_json/{0}'.format(imdbid)
        dq.push(url)

    while True:
        time.sleep(0.1)
        try:
            print(dq.pop())
        except LookupError as le:
            print(le)
