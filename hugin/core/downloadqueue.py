#/usr/bin/env python
# encoding: utf-8

""" This module encapsulates a thread-based downloadqueue. """

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from queue import Queue, Empty

import charade
import httplib2


class DownloadQueue:

    """ A simple queue/threadpool wrapper for simultanous downloading using."""

    def __init__(
            self, num_threads=4, user_agent='libhugin/1.0', timeout_sec=5,
            local_cache=None):
        """
        Set custom downlodqueue parameters.

        :param num_threads: Number of threads for simultanous downloading.
        :param user_agent: User-Agent to be used.
        :param timeout: Url timeout to be used for each url.
        :param local_cache: A local cache for lookup before download.

        """
        self._num_threads = num_threads if num_threads <= 10 else 10
        self._headers = {'User-Agent': user_agent, 'Connection': 'close'}
        self._timeout_sec = timeout_sec
        self._local_cache = None
        if local_cache is not None:
            self._local_cache = local_cache

        self._url_to_provider_data_lock = Lock()
        self._url_to_provider_data = {}
        self._request_queue = Queue()

        self._executor = ThreadPoolExecutor(max_workers=self._num_threads)
        self._shutdown_downloadqueue = False
        self._is_shutdown = False

    def _shutdown(self):
        """ Stop the ThreadPool and wait until pending jobs are done. """
        self._executor.shutdown(wait=True)
        self._is_shutdown = True

    def _fetch_url(self, url, timeout_sec):
        """
        Get the requested url from cache or web.

        :param url: A absolute URI that starts with http/https.
        :param timeout_sec: A timeout to be used for each request.

        """
        resp, content = None, None
        try:
            if self._local_cache is not None:
                # we use 0 as status code for local fetch
                resp, content = 0, self._local_cache.read(url)
            # if nothing found in local cache
            if content is None:
                http = httplib2.Http(timeout=timeout_sec)
                resp, content = http.request(uri=url, headers=self._headers)
        except httplib2.RelativeURIError:
            print('RelativeURIError')
        except Exception as e:
            print('Something went terribly wrong!', e)

        with self._url_to_provider_data_lock:
            provider_data = self._url_to_provider_data.pop(url)
            if resp == 0:
                provider_data['response'] = content
                provider_data['return_code'] = resp
                provider_data['cache_used'] = True
            else:
                try:
                    provider_data['return_code'] = resp.status
                    provider_data['response'] = self._bytes_to_unicode(content)
                except AttributeError:
                    print('AttributeError')
                except Exception as e:
                    print('Something went terribly wrong!', e)
            self._request_queue.put(provider_data)

    def _bytes_to_unicode(self, byte_data):
        """
        Decode a http byte-response to unicode.

        Tries to decode bytestream to utf-8. If this fails, encoding is guessed
        by charade and decoding is repeated with just dedected encoding.

        :param byte_data: A bytestream.
        :returns: A unicode

        """
        try:
            return byte_data.decode('utf-8')
        except (TypeError, AttributeError) as e:
            print(e, 'trying to use charade now to quess encoding.')
            encoding = charade.detect(byte_data).get('encoding')
            return byte_data.decode(encoding)

    def push(self, provider_data):
        """
        Execute a asynchronous download job.

        :param provider_data: A provider_data object.

        """

        if provider_data is None and self._shutdown_downloadqueue is False:
            self._shutdown_downloadqueue = True
            self._shutdown()

        if self._shutdown_downloadqueue is False:
            url = provider_data['url']
            if url and url not in self._url_to_provider_data:

                with self._url_to_provider_data_lock:
                    self._url_to_provider_data[url] = provider_data

                provider_data['future'] = self._executor.submit(
                    self._fetch_url,
                    url=url,
                    timeout_sec=self._timeout_sec
                    )

    def pop(self):
        """
        Get the a finished provider_data object.

        :returns: Next avaiable provider data object.
        :raises:  Empty exception if queue is empty.

        """
        try:
            return self._request_queue.get_nowait()
        except Empty:
            if len(self._url_to_provider_data) == 0:
                raise Empty
            else:
                return self._request_queue.get()

    def running_jobs(self):
        """
        Get count of 'jobs' in download queue.

        :returns: Sum of jobs in queue and pending/active jobs

        """
        return self._request_queue.qsize() + len(self._url_to_provider_data)


if __name__ == '__main__':
    from hugin.core.cache import Cache
    import json
    import unittest

    class TestDownloadQueue(unittest.TestCase):

        def setUp(self):
            # download queue with default setting
            self._dq_default = DownloadQueue(user_agent='katzenbaum/4.2')
            # cache for custom downlodqueue
            self._cache = Cache()
            self._cache.open()
            self._dq_custom = DownloadQueue(
                local_cache=self._cache
            )
            self._url = 'http://httpbin.org/status/{code}'
            self._provider_data = {
                'url': 'http://httpbin.org/get',
                'response': None,
                'return_code': None
            }

        def test_user_agent(self):
            self._dq_default.push(self._provider_data)
            provider_data = self._dq_default.pop()
            response = json.loads(provider_data['response'])
            self.assertTrue(
                response['headers']['User-Agent'] == 'katzenbaum/4.2'
            )

        def test_bad_status_codes(self):
            test_codes = [404, 408, 503]
            for status_code in test_codes:
                self._provider_data['url'] = self._url.format(code=status_code)
                self._dq_default.push(self._provider_data)
                provider_data = self._dq_default.pop()

                self.assertTrue(provider_data['return_code'] in test_codes)
                self.assertTrue(provider_data['response'] is '')
                test_codes.remove(status_code)

        def test_good_status_codes(self):
            test_codes = [200, 300, 304, 307]

            for status_code in test_codes:
                self._provider_data['url'] = self._url.format(code=status_code)
                self._provider_data['response'] = None

                self._dq_default.push(self._provider_data)
                provider_data = self._dq_default.pop()

                self.assertTrue(provider_data['return_code'] in test_codes)
                test_codes.remove(status_code)
                self.assertTrue(provider_data['response'] is not None)

        def test_without_local_cache(self):
            self._dq_default.push(self._provider_data)
            provider_data = self._dq_default.pop()
            self._dq_default.push(self._provider_data)
            provider_data = self._dq_default.pop()

            self.assertTrue(provider_data['return_code'] != 0)
            self.assertTrue(provider_data['return_code'] == 200)

        def test_with_local_cache(self):
            self._dq_default.push(self._provider_data)
            provider_data = self._dq_default.pop()
            self.assertTrue(provider_data['return_code'] == 200)

            self._cache.write(provider_data['url'], provider_data['response'])

            self._dq_custom.push(provider_data)
            provider_data = self._dq_custom.pop()
            self.assertTrue(provider_data['return_code'] == 0)

        def test_pop_empty(self):
            with self.assertRaises(Empty):
                self._dq_default.pop()

        def test_downloadqueue_shutdown(self):
            self.assertTrue(self._dq_default._is_shutdown is False)
            self._dq_default.push(None)
            self.assertTrue(self._dq_default._is_shutdown is True)

            self.assertTrue(self._dq_custom._is_shutdown is False)
            self._dq_custom.push(self._provider_data)
            self.assertTrue(self._dq_custom._is_shutdown is False)
            self._dq_default.push(None)
            self._dq_default.push(None)
            self._dq_default.push(None)
            self.assertTrue(self._dq_default._is_shutdown is True)

        def tearDown(self):
            self._cache.close()

    unittest.main()
