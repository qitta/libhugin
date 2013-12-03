#!/usr/bin/env python
# encoding: utf-8

""" Session and query handling. """

from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from itertools import zip_longest
from functools import reduce
from threading import Lock
from operator import add
import sys
import queue
import signal

from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloadqueue import DownloadQueue
from hugin.core.provider.result import Result
from hugin.core.cache import Cache
from hugin.query import Query


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
        if self._shutdown_session:
            self.clean_up()
        else:
            results = []
            downloadqueue = self._init_download_queue(query)

            for job in self._create_jobs_according_to_search_params(query):
                if job['is_done']:
                    results.append(self._job_to_result(job, query))
                else:
                    downloadqueue.push(job)

            while True:
                try:
                    job = downloadqueue.pop()
                except queue.Empty:
                    break

                # trigger provider to parse its request and process the result
                job['result'], job['is_done'] = job['provider'].parse_response(
                    job['response'], query
                )

                if job['is_done']:
                    self._process_flagged_as_done(
                        job, downloadqueue, query, results
                    )
                else:
                    self._process_flagged_as_not_done(
                        job, downloadqueue, query, results
                    )

            downloadqueue.push(None)
            return self._select_results_by_strategy(results, query)

    def submit_async(self, query):
        future = self._async_executor.submit(
            self.submit,
            query
        )
        self._futures.append(future)
        return future

    def _process_flagged_as_done(self, job, downloadqueue, query, results):
        if job['is_done'] or job['result'] == []:
            if job['result'] is not None:
                self._add_to_cache(job)
            results.append(self._job_to_result(job, query))

    def _process_flagged_as_not_done(self, job, downloadqueue, query, results):
        if job['result'] and job['is_done'] is False:
            self._add_to_cache(job)
            new_jobs = self._create_new_jobs_from_result(job, query)
            for job in new_jobs:
                downloadqueue.push(job)

        if job['result'] is None and job['is_done'] is False:
            job = self._decrement_retries(job)
            if job['is_done']:
                results.append(self._job_to_result(job, query))
            else:
                downloadqueue.push(job)

    def _select_results_by_strategy(self, results, query):
        if query['strategy'] == 'deep':
            return self._results_deep_strategy(results, query)
        else:
            return self._results_flat_strategy(results, query)

    def _results_flat_strategy(self, results, query):
        result_map = defaultdict(list)
        for result in results:
            result_map[result.provider].append(result)
        results = list(
            filter(None, reduce(add, zip_longest(*result_map.values())))
        )
        return results[0:query['items']]

    def _results_deep_strategy(self, results, query):
        results.sort(key=lambda x: x.provider._priority, reverse=True)
        return results[0:query['items']]

    def _job_to_result(self, job, query):
        retries = query['retries'] - job['retries_left']
        result = Result(
            provider=job['provider'],
            query=query,
            result=job['result'],
            retries=retries
        )
        return result

    def _decrement_retries(self, job):
        if job['retries_left'] > 0:
            job['retries_left'] -= 1
        else:
            job['is_done'] = True
        return job

    def _get_job_struct(self, provider, query):
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

    def _create_jobs_according_to_search_params(self, query):
        providers = []
        for key, value in self._provider_types.items():
            if query['type'] in key:
                providers += self._provider_types[key]

        job_list = []
        for provider in providers:
            provider = provider['name']
            job = self._get_job_struct(provider=provider, query=query)
            url_list = job['provider'].build_url(query)

            if url_list is not None:
                job['url'] = url_list
            else:
                job['is_done'] = True
            job_list.append(job)

        return job_list

    def _create_new_jobs_from_result(self, job, query):
        urllist = []
        for url_list in job['result']:
            job = self._get_job_struct(provider=job['provider'], query=query)
            job['url'] = url_list
            urllist.append(job)
        return urllist

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
