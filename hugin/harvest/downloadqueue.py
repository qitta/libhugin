#/usr/bin/env python
# encoding: utf-8

""" This module encapsulates a thread-based downloadqueue. """

# stdlib
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Lock

# 3rd party
import charade
import httplib2


class DownloadQueue:

    """ A simple queue/threadpool wrapper for simultanous downloading.

    .. autosummary::


        push
        pop
        running_jobs

    """
    def __init__(
            self, num_threads=4, user_agent='libhugin/1.0', timeout_sec=5,
            local_cache=None):
        """
        .. todo:: REAL DQ threads, not job sreds!

        Set custom downlodqueue parameters.

        :param num_threads: Number of threads for simultanous downloading.
        :param user_agent: User-Agent to be used.
        :param timeout: Url timeout to be used for each http request.
        :param local_cache: A local cache for lookup before download.

        """
        self._num_threads = min(num_threads, 10)
        self._headers = {
            'User-Agent': user_agent,
            'Connection': 'close',
            'cache-control': 'no-cache'
        }
        self._timeout_sec = timeout_sec
        self._local_cache = local_cache
        self._url_to_job_lock = Lock()
        self._url_to_job = {}
        self._job_result_queue = Queue()

        self._executor = ThreadPoolExecutor(max_workers=self._num_threads)
        self._shutdown_downloadqueue = False

    def _shutdown(self):
        """ Stop the ThreadPool and wait until pending jobs are done. """
        self._executor.shutdown(wait=True)

    def _fetch_url(self, url, timeout_sec):
        """ Fetch a specific url.

        If cache is available, that a cache lookup is done first, otherwise
        download is triggerd.

        :param url: Url to fetch.
        :param timeout_sec: Timeout for http request.
        :returns: A tuple with the header and http response

        """
        header, content = None, None
        try:
            if self._local_cache is not None:
                header, content = 'local', self._local_cache.read(url)

            if content is None:
                http = httplib2.Http(timeout=timeout_sec)
                header, content = http.request(uri=url, headers=self._headers)

        except httplib2.HttpLib2Error as e:
            print('Httplib2 Error', e)
        except OSError as e:
            print('A Exception occured', e)
        except Exception as e:
            print('Uncaught Exception? in full job response.', e)
        return header, content

    def _fetch_urllist(self, urls, timeout_sec):
        """
        Download urls, fill job struct and add job to job_result_queue.

        1.) Urls are fetched
        2.) Jobs are filled in with http responses
        3.) Jobs are pushed to job_result_queue

        :param urls: A list with urls to fetch.
        :param timeout_sec: A timeout to be used for http request.

        """
        response_list = []

        for url in urls:
            header, content = self._fetch_url(url, timeout_sec)
            content = (url, content)
            response_list.append((header, content))

        with self._url_to_job_lock:
            job = self._url_to_job.pop(id(urls))
        job = self._fill_job_response(job, response_list)
        self._job_result_queue.put(job)

    def _fill_job_response(self, job, response_list):
        """
        Fills job with response data.

        .. todo:: cache_use und return_code spezifizieren und vollständig machen.

        """
        job.response, job.return_code, job.cache_used = [], [], []

        for response_item in response_list:
            header, url_content = response_item
            url, content = url_content
            if header == 'local':
                job.response.append(url_content)
                job.return_code.append(header)
                job.cache_used.append((url, True))
            elif content:
                job.response.append(
                    (url, self._bytes_to_unicode(content))
                )
                job.return_code.append(header)
                job.cache_used.append((url, False))

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
        except (TypeError, AttributeError, UnicodeError) as e:
            print('Error decoding bytes to utf-8.', e)

        try:
            encoding = charade.detect(byte_data).get('encoding')
            return byte_data.decode(encoding)
        except (TypeError, AttributeError, UnicodeError) as e:
            print('Error decoding bytes after charade  detection to utf-8.', e)

    def push(self, job):
        """
        Execute a asynchronous download job.

        :param job: A job dict structure.

        """
        if job is None and self._shutdown_downloadqueue is False:
            self._shutdown_downloadqueue = True
            self._shutdown()

        if self._shutdown_downloadqueue is False:
            urls = job.url
            id_urllist = id(urls)

            with self._url_to_job_lock:
                in_url_to_job = id_urllist in self._url_to_job

            if urls and not in_url_to_job:
                with self._url_to_job_lock:
                    self._url_to_job[id_urllist] = job
                job.future = self._executor.submit(
                    self._fetch_urllist,
                    urls=urls,
                    timeout_sec=self._timeout_sec
                )

    def pop(self):
        """
        Get the a finished job.

        :returns: Next avaiable provider data object.
        :raises:  Empty exception if queue is empty.

        """
        try:
            return self._job_result_queue.get_nowait()
        except Empty:
            if len(self._url_to_job) == 0:
                raise Empty
            else:
                return self._job_result_queue.get()

    def running_jobs(self):
        """
        Get count of 'jobs' in download queue.

        :returns: Sum of jobs in queue and pending/active jobs

        """
        return self._job_result_queue.qsize() + len(self._url_to_job)


if __name__ == '__main__':
    from hugin.harvest.cache import Cache
    import json
    import unittest
    import types

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
            self._job = types.SimpleNamespace(**{
                'url': ['http://httpbin.org/get'],
                'response': None,
                'return_code': None
            })

        def test_user_agent(self):
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            for url, content in job.response:
                response = json.loads(content)
                self.assertTrue(
                    response['headers']['User-Agent'] == 'katzenbaum/4.2'
                )

        def test_bad_status_codes(self):
            test_codes = ['404', '408', '503']
            self._job.url = [
                self._url.format(code=_code) for _code in test_codes
            ]
            self._dq_default.push(self._job)
            job = self._dq_default.pop()

            for code in job.return_code:
                self.assertTrue(code['status'] in test_codes)
                test_codes.remove(code['status'])

            for response in job.response:
                url, content = response
                self.assertTrue(content is '')

        def test_good_status_codes(self):
            test_codes = ['200', '300', '304']

            self._job.url = [
                self._url.format(code=_code) for _code in test_codes
            ]
            self._job.response = None

            self._dq_default.push(self._job)
            job = self._dq_default.pop()

            for code in job.return_code:
                self.assertTrue(code['status'] in test_codes)
                test_codes.remove(code['status'])

            for response in job.response:
                url, content = response
                self.assertTrue(content is '')

        def test_without_local_cache(self):
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            for code in job.return_code:
                self.assertTrue(code != 'local')
                self.assertTrue(code['status'] == '200')

        def test_with_local_cache(self):
            self._dq_default.push(self._job)
            job = self._dq_default.pop()
            for code in job.return_code:
                self.assertTrue(code['status'] == '200')

            for url, content in job.response:
                self._cache.write(url, content)
        #    self._cache.write(job.url, job.response)

            self._dq_custom.push(job)
            job = self._dq_custom.pop()

            for code in job.return_code:
                self.assertTrue(code == 'local')

        def test_pop_empty(self):
            with self.assertRaises(Empty):
                self._dq_default.pop()

        def test_downloadqueue_shutdown(self):
            self.assertTrue(self._dq_default._shutdown_downloadqueue is False)
            self._dq_default.push(None)
            self.assertTrue(self._dq_default._shutdown_downloadqueue is True)

            self.assertTrue(self._dq_custom._shutdown_downloadqueue is False)
            self._dq_custom.push(self._job)
            self.assertTrue(self._dq_custom._shutdown_downloadqueue is False)
            self._dq_default.push(None)
            self._dq_default.push(None)
            self._dq_default.push(None)
            self.assertTrue(self._dq_default._shutdown_downloadqueue is True)

        def tearDown(self):
            self._cache.close()

    unittest.main()
