#/usr/bin/env python
# encoding: utf-8

""" This module encapsulates a thread-based downloadqueue. """

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from queue import Queue, Empty
from socket import timeout

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
        self._num_threads = min(num_threads, 10)
        self._headers = {
            'User-Agent': user_agent,
            'Connection': 'close',
            'cache-control': 'no-cache'
        }
        self._timeout_sec = timeout_sec
        self._local_cache = None
        if local_cache is not None:
            self._local_cache = local_cache

        self._url_to_job_lock = Lock()
        self._url_to_job = {}
        self._request_queue = Queue()

        self._executor = ThreadPoolExecutor(max_workers=self._num_threads)
        self._shutdown_downloadqueue = False
        self._is_shutdown = False

    def _shutdown(self):
        """ Stop the ThreadPool and wait until pending jobs are done. """
        self._executor.shutdown(wait=True)
        self._is_shutdown = True

    def _fetch_url(self, url, timeout_sec):
        header, content = None, None
        try:
            if self._local_cache is not None:
                header, content = 'local', self._local_cache.read(url)

            if content is None:
                http = httplib2.Http(timeout=timeout_sec)
                header, content = http.request(uri=url, headers=self._headers)

        except httplib2.RelativeURIError as e:
            print('RelativeURIError', e, header, content)
        except timeout as e:
            print('Something went terribly wrong! TIMEOUT', url)
        except Exception as e:
            print('Something went terribly wrong!', url, header, content)
        return header, content

    def _fetch_urllist(self, urllist, timeout_sec):
        """
        Get the requested url from cache or web.

        :param url: A absolute URI that starts with http/https.
        :param timeout_sec: A timeout to be used for each request.

        """
        response_list = []

        for url in urllist:
            header, content = self._fetch_url(url, timeout_sec)
            content = (url, content)
            response_list.append((header, content))

        with self._url_to_job_lock:
            job = self._url_to_job.pop(id(urllist))
            job = self._fill_job_response(job, response_list)
            self._request_queue.put(job)

    def _fill_job_response(self, job, response_list):
        job['response'], job['return_code'], job['cache_used'] = [], [], []

        for response_item in response_list:
            header, url_content = response_item
            url, content = url_content
            if header == 'local':
                job['response'].append(url_content)
                job['return_code'].append(header)
                job['cache_used'].append((url, True))
            else:
                if content is not None:
                    try:
                        job['response'].append(
                            (url, self._bytes_to_unicode(content))
                        )
                        job['return_code'].append(header)
                        job['cache_used'].append((url, False))
                    except AttributeError:
                        print('AttributeError')
                    except Exception as e:
                        print('Something went terribly wrong!', e, header, content)
        return job

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

    def push(self, job):
        """
        Execute a asynchronous download job.

        :param job: A job object.

        """
        if job is None and self._shutdown_downloadqueue is False:
            self._shutdown_downloadqueue = True
            self._shutdown()

        if self._shutdown_downloadqueue is False:
            urllist = job['url']
            id_urllist = id(urllist)
            if urllist and id_urllist not in self._url_to_job:

                with self._url_to_job_lock:
                    self._url_to_job[id_urllist] = job
                job['future'] = self._executor.submit(
                    self._fetch_urllist,
                    urllist=urllist,
                    timeout_sec=self._timeout_sec
                )

    def pop(self):
        """
        Get the a finished job object.

        :returns: Next avaiable provider data object.
        :raises:  Empty exception if queue is empty.

        """
        try:
            return self._request_queue.get_nowait()
        except Empty:
            if len(self._url_to_job) == 0:
                raise Empty
            else:
                return self._request_queue.get()

    def running_jobs(self):
        """
        Get count of 'jobs' in download queue.

        :returns: Sum of jobs in queue and pending/active jobs

        """
        return self._request_queue.qsize() + len(self._url_to_job)


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
            self._job = {
                'url': ['http://httpbin.org/get'],
                'response': None,
                'return_code': None
            }

        def test_user_agent(self):
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            for url, content in job['response']:
                response = json.loads(content)
                self.assertTrue(
                    response['headers']['User-Agent'] == 'katzenbaum/4.2'
                )

        def test_bad_status_codes(self):
            test_codes = ['404', '408', '503']
            self._job['url'] = [
                self._url.format(code=_code) for _code in test_codes
            ]
            self._dq_default.push(self._job)
            job = self._dq_default.pop()

            for code in job['return_code']:
                self.assertTrue(code['status'] in test_codes)
                test_codes.remove(code['status'])

            for response in job['response']:
                url, content = response
                self.assertTrue(content is '')

        def test_good_status_codes(self):
            test_codes = ['200', '300', '304']

            self._job['url'] = [
                self._url.format(code=_code) for _code in test_codes
            ]
            self._job['response'] = None

            self._dq_default.push(self._job)
            job = self._dq_default.pop()

            for code in job['return_code']:
                self.assertTrue(code['status'] in test_codes)
                test_codes.remove(code['status'])

            for response in job['response']:
                url, content = response
                self.assertTrue(content is '')


        def test_without_local_cache(self):
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            for code in job['return_code']:
                self.assertTrue(code != 'local')
                self.assertTrue(code['status'] == '200')

        def test_with_local_cache(self):
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            for code in job['return_code']:
                self.assertTrue(code['status'] == '200')

            for url, content in job['response']:
                self._cache.write(url, content)
        #    self._cache.write(job['url'], job['response'])

            self._dq_custom.push(job)
            job = self._dq_custom.pop()

            for code in job['return_code']:
                self.assertTrue(code == 'local')

        def test_pop_empty(self):
            with self.assertRaises(Empty):
                self._dq_default.pop()

        def test_downloadqueue_shutdown(self):
            self.assertTrue(self._dq_default._is_shutdown is False)
            self._dq_default.push(None)
            self.assertTrue(self._dq_default._is_shutdown is True)

            self.assertTrue(self._dq_custom._is_shutdown is False)
            self._dq_custom.push(self._job)
            self.assertTrue(self._dq_custom._is_shutdown is False)
            self._dq_default.push(None)
            self._dq_default.push(None)
            self._dq_default.push(None)
            self.assertTrue(self._dq_default._is_shutdown is True)

        def tearDown(self):
            self._cache.close()

    unittest.main()
