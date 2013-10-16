#/usr/bin/env python
# encoding: utf-8

from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Lock
from queue import Queue, Empty
import requests


USER_AGENT = "libhugin 'rebellic raven'/0.1"


class DownloadQueue:
    def __init__(self, num_threads=20, user_agent=USER_AGENT, timeout=5):
        '''
        A simple multithreaded add/get download queue wrapper using standard
        queue and future-requests

        :param num_threads: Number of threads to be used for simultanous
                            downloading
        '''
        self._url_to_provider_data_lock = Lock()
        self._session = FuturesSession(
            executor=ThreadPoolExecutor(max_workers=num_threads)
        )
        self._session.headers['User-Agent'] = user_agent
        self._request_queue = Queue()
        self._url_to_provider_data = {}
        self._timeout = timeout

    def push(self, provider_data):
        '''
        Feeds DownloadQueue with url to fetch
        //TODO: Exchange url with ProviderDataObject

        :param url: Given url to be downloaded
        '''
        with self._url_to_provider_data_lock:
            url = provider_data['url']
            if url not in self._url_to_provider_data:
                future = self._session.get(
                    url,
                    timeout=self._timeout,
                    background_callback=partial(
                        self._response_finished,
                        url=url
                    )
                )
                provider_data['future'] = future
                self._url_to_provider_data[url] = provider_data

    def pop(self):
        '''
        Simple DownloadQueue getter

        :returns: Next avaiable response object.
        :raises:  LookupError if queue is empty.
        '''
        try:
            return self._request_queue.get(timeout=0.5)
        except Empty:
            if len(self._url_to_provider_data) > 0:
                self._get_stalled_futures()
            else:
                raise LookupError('download queue is empty.')

    def _get_stalled_futures(self):
        '''
        Checks futures dictionary for stalled or timeouted futures.

        :returns: Future result, if a timeout occured, 'timeout' is returned.
        :raises:  LookupError if queue is empty and no futures are done.
        '''
        with self._url_to_provider_data_lock:
            stalled_urls = []
            for url, provider_data in self._url_to_provider_data.items():
                if provider_data['future'].done() is True:
                    stalled_urls.append(url)
                else:
                    raise LookupError('no url done yet.')
            for url in stalled_urls:
                result = self._url_to_provider_data.pop(url)
                result['response'] = 'invalid.'
                self._request_queue.put(result)

    def _response_finished(self, _, response, url):
        '''
        :param response: Finished response object
        :param url: Given url to download
        '''
        with self._url_to_provider_data_lock:
            provider_data = self._url_to_provider_data.pop(url)
            provider_data['response'] = response
            provider_data['future'] = None
            self._request_queue.put(provider_data)
