#!/usr/bin/env python
# encoding: utf-8

""" Session and query handling. """


from concurrent.futures import ThreadPoolExecutor
from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloadqueue import DownloadQueue
from hugin.query import Query
from hugin.core.provider.result import Result
from hugin.core.cache import Cache
from threading import Lock
import sys
import queue
import signal


class Session:
    def __init__(
        self, cache_path='/tmp', parallel_jobs=1,
        timeout_sec=5, user_agent='libhugin/1.0', use_cache='True'
    ):
        self._config = {
            'cache_path': cache_path,
            # limit parallel jobs to 4, there is no reason for a huge number of
            # parallel jobs because of the GIL
            'parallel_jobs': min(4, parallel_jobs),
            'timeout_sec': timeout_sec,
            'user_agent': user_agent,
            'profile': {
                'default': [],
                'search_pictures': False,
                'search_text': True
            }
        }

        self._plugin_handler = PluginHandler()
        self._plugin_handler.activate_plugins_by_category('Provider')
        self._plugin_handler.activate_plugins_by_category('Postprocessing')
        self._provider = self._plugin_handler.get_plugins_from_category(
            'Provider'
        )
        self._postprocessing = self._plugin_handler.get_plugins_from_category(
            'Postprocessing'
        )
        self._converter = self._plugin_handler.get_plugins_from_category(
            'OutputConverter'
        )
        self._cache = Cache()
        self._cache.open()
        self._async_executor = ThreadPoolExecutor(
            max_workers=4
        )

        self._cleanup_triggered = False
        self._provider_types = {
            'movie': [],
            'movie_picture': [],
            'person': [],
            'person_picture': []
        }
        self._downloadqueues = []
        self._futures = []
        self._shutdown_session = False
        self._global_session_lock = Lock()

        # categorize provider for convinience reasons
        for provider in self._provider:
            self._categorize(provider)

    def create_query(self, **kwargs):
        return Query(kwargs)

    def _init_download_queue(self, query):
        if query['use_cache'] is False:
            query['use_cache'] = None
        else:
            print('cache enabled.')
            query['use_cache'] = self._cache

        downloadqueue = DownloadQueue(
            num_threads=self._config['parallel_jobs'],
            timeout_sec=self._config['timeout_sec'],
            user_agent=self._config['user_agent'],
            local_cache=query['use_cache']
        )
        self._downloadqueues.append(downloadqueue)
        return downloadqueue

    def _add_to_cache(self, job):
        for url, data in job['response']:
            self._cache.write(url, data)

    def submit(self, query):
        finished_jobs = []
        download_queue = None

        if self._shutdown_session is False:
            download_queue = self._init_download_queue(query)

            jobs = self._process_new_query(query)
            for job in jobs:
                if job['is_done']:
                    finished_jobs.append(self._job_to_result(job, query))
                else:
                    download_queue.push(job)

            while True:
                try:
                    job = download_queue.pop()
                except queue.Empty:
                    break

                result, state = job['provider'].parse_response(
                    job['response'], query
                )
                job['result'], job['is_done'] = result, state

                if state is True or result == []:
                    if result is not None:
                        self._add_to_cache(job)
                    finished_jobs.append(self._job_to_result(job, query))
                else:
                    if result is None:
                        job = self._check_for_retry(job)
                        if job['is_done']:
                            finished_jobs.append(
                                self._job_to_result(job, query)
                            )
                        else:
                            download_queue.push(job)
                    else:
                        self._add_to_cache(job)
                        new_jobs = self._process(job, query)
                        for job in new_jobs:
                            download_queue.push(job)
            download_queue.push(None)
            if query['imdbid'] is None:
                finished_jobs = self._filter_finished(finished_jobs, query)

        else:
            self.clean_up()
            self._downloadqueues.remove(download_queue)
        return finished_jobs

    def _filter_finished(self, jobs, query):
        jobs.sort(key=lambda x: x.provider._priority, reverse=True)
        return jobs[0:query['items']]

    def _job_to_result(self, job, query):
        retries = query['retries'] - job['retries_left']
        result = Result(
            provider=job['provider'],
            query=query,
            result=job['result'],
            retries=retries
        )
        return result

    def _check_for_retry(self, job):
        if job['retries_left'] > 0:
            job['retries_left'] -= 1
        else:
            job['is_done'] = True
        return job

    def get_job_struct(self, provider, query):
        return {
            'url': None,
            'provider': provider,
            'future': None,
            'response': None,
            'is_done': False,
            'result': None,
            'return_code': None,
            'retries_left': query.get('retries')
        }

    def _process_new_query(self, query):
        providers = []
        for key, value in self._provider_types.items():
            if query['type'] in key:
                providers += self._provider_types[key]
        job_list = []

        for provider in providers:
            provider = provider['name']
            job = self.get_job_struct(provider=provider, query=query)
            url_list = job['provider'].build_url(query)

            # result should be a list with urls
            if url_list is not None:
                job['url'] = url_list
            else:
                job['is_done'] = True
            job_list.append(job)

        return job_list

    def _process(self, job, query):
        new_jobs = []
        for url_list in job['result']:
            job = self.get_job_struct(
                provider=job['provider'],
                query=query
            )
            job['url'] = url_list
            new_jobs.append(job)
        return new_jobs

    def submit_async(self, query):
        future = self._async_executor.submit(
            self.submit,
            query
        )
        self._futures.append(future)
        return future

    def providers_list(self, category=None):
        if category and category in self._provider_types:
            return self._provider_types[category]
        else:
            return self._provider_types

    def provider_types(self):
        return self._provider_types.keys()

    def _categorize(self, provider):
        self._provider_types[provider.identify_type()].append(
            {'name': provider, 'supported_attrs': provider.supported_attrs}
        )

    def get_providers(self):
        return self._provider_types

    def get_provider(self, name):
        extract_provider += [y for z, y in self._provider_types.items()]
        for item in extract_provider:
            print(item['name'])

    def get_postprocessing(self):
        return self._postprocessing

    def converter_list(self):
        pass

    def config_list(self):
        return self._config

    def clean_up(self):
        """ Do a clean up on keyboard interrupt or submit cancel. """
        if self._cleanup_triggered is False:
            self._cleanup_triggered = True
            print('You pressed Ctrl+C!')
            print('cleaning  up.')
            # kill all pending futures
            for future in self._futures:
                if future.running() is False and future.done() is False:
                    future.cancel()
            print('waiting for remaining futures to complete.')
            self._async_executor.shutdown(wait=True)
            print('closing cache.')
            self._cache.close()
            print('cache closed.')
            sys.exit(1)

    def cancel(self):
        """ Cancel the currently running session. """
        self._shutdown_session = True

    def signal_handler(self, signal, frame):
        self.cancel()

if __name__ == '__main__':

    def read_list_async():
        hs = Session(parallel_jobs=5, timeout_sec=5)
        signal.signal(signal.SIGINT, hs.signal_handler)
        f = open('./hugin/core/testdata/imdbid_small.txt').read().splitlines()
        futures = []
        f = [2]
        for imdbid in f:
            q = hs.create_query(
                type='movie',
                search_text=True,
                use_cache=False,
                name='Sin City'
            )
            futures.append(hs.submit_async(q))

        while len(futures) > 0:
            for item in futures:
                if item.done():
                    try:
                        t = item.result()
                        print(100 * '-')
                        print(t)
                    except:
                        pass
                    futures.remove(item)
        hs._cache.close()

    def read_list_sync():
        hs = Session(parallel_jobs=5, timeout_sec=5)
        signal.signal(signal.SIGINT, hs.signal_handler)
        f = open('./hugin/core/testdata/imdbid_huge.txt').read().splitlines()
        f = ['tt2524674']
        for imdbid in f:
            q = hs.create_query(
                type='movie',
                search_text=True,
                use_cache=False,
                search_pictures=True,
                language='de',
                retries=5,
                title='Feuchtgebiete',
                items=3
            )
            result_list = hs.submit(q)
            print(100 * '-')
            pp, *other = hs.get_postprocessing()
            custom = pp.create_custom(result_list)
            result_list += custom
            for item in result_list:
                if item.is_valid():
                    print(item)
                    print('title:', item._result_dict['title'], item._result_dict['genre_norm'], item._result_dict['imdbid'])
                    print(item._result_dict['plot'])
                    print()
                    print(100 * '-')
        hs._cache.close()
    try:
        read_list_sync()
    except KeyboardInterrupt:
        print('Interrupted by user.')
