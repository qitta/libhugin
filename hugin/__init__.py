#!/usr/bin/env python
# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor
from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloader import DownloadQueue
from hugin.providerdata import ProviderData
from hugin.query import Query
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
            'parallel_jobs': 4 if parallel_jobs <= 4 else 4,
            'timeout_sec': timeout_sec,
            'user_agent': user_agent,
            'profile': {
                'default': [],
                'search_pictures': False,
                'search_text': True
            }
        }
        self._query_attrs = [
            'title', 'year', 'name', 'imdbid', 'type', 'search_text',
            'language', 'seach_picture', 'items', 'use_cache'
        ]
        self._plugin_handler = PluginHandler()
        self._plugin_handler.activate_plugins_by_category('Provider')
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
            max_workers=self._config['parallel_jobs']
        )

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
        [self._categorize(provider) for provider in self._provider]

    def create_query(self, **kwargs):
        return Query(self._query_attrs, kwargs)

    def _init_download_queue(self, query):
        if query['use_cache'] is False:
            query['use_cache'] = None
        else:
            query['use_cache'] = self._cache

        downloadqueue = DownloadQueue(
            num_threads=self._config['parallel_jobs'],
            timeout_sec=self._config['timeout_sec'],
            user_agent=self._config['user_agent'],
            local_cache=query['use_cache']
        )
        self._downloadqueues.append(downloadqueue)
        return downloadqueue

    def submit(self, query):
        finished_jobs = []
        download_queue = self._init_download_queue(query)

        jobs = self._process_new_query(query)
        [download_queue.push(provider_data) for provider_data in jobs]

        while True: # self._shutdown_session is False:
            # wait for next provider_data
            try:
                provider_data = download_queue.pop()
            except queue.Empty:
                break

            if provider_data['return_code'] in [408]:
                provider_data.decrement_retries()
                if provider_data['is_done']:
                    finished_jobs.append(provider_data)
                else:
                    download_queue.push(provider_data)
            else:
                provider_data.invoke_parse()
                if provider_data.is_done:
                    self._cache.write(
                        provider_data['url'],
                        provider_data['response']
                    )
                    finished_jobs.append(provider_data)
                else:
                    new = self._process(provider_data)
                    for provider_data in new:
                        if provider_data['is_done']:
                            finished_jobs.append(provider_data)
                        else:
                            download_queue.push(provider_data)
        with self._global_session_lock:
            download_queue.push(None)
            if self._shutdown_session is True:
                self.clean_up()
                print('SIZE:', download_queue.running_jobs())
                self._downloadqueues.remove(download_queue)
        return finished_jobs


    def _process_new_query(self, query):
        providers = self._provider_types[query['type']]
        provider_data_list = []
        for provider in providers:
            provider = provider['name']
            provider_data = ProviderData(provider=provider, query=query)
            provider_data.invoke_search()
            provider_data_list.append(provider_data)
        return provider_data_list

    def _process(self, provider_data):
        new_jobs = []

        if provider_data['result'] is None:
            provider_data.decrement_retries()
            new_jobs.append(provider_data)
        else:
            self._cache.write(
                provider_data['url'],
                provider_data['response']
            )
            for url in provider_data['result']:
                provider_data = ProviderData(
                    provider=provider_data['provider'],
                    url=url,
                    query=provider_data['query']
                )
                new_jobs.append(provider_data)
            # that provider data object seems to be valid, lets cache it
        return new_jobs

    def submit_async(self, query):
        if self._shutdown_session is False:
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

    def result_attributes(self):
        pass

    def _categorize(self, provider):
        self._provider_types[provider.identify_type()].append(
            {'name': provider, 'supported_attrs': provider.supported_attrs}
        )

    def converter_list(self):
        pass

    def config_list(self):
        return self._config

    def cancel(self):
        self._shutdown_session = True

    def clean_up(self):
        futures_cancelled = []
        # kill all pending futures
        for future in self._futures:
            if future.running() is False and future.done() is False:
                future.cancel()
        self._async_executor.shutdown(wait=False)
        self._cache.close()
        sys.exit(1)

    def handler(self, signal, frame):
        # print('You pressed Ctrl+C!')
        self._shutdown_session = True

if __name__ == '__main__':
    hs = Session(parallel_jobs=1, timeout_sec=5)
    signal.signal(signal.SIGINT, hs.handler)
    f = open('./hugin/core/testdata/imdbid_huge.txt').read().splitlines()
    # print(hs.providers_list())
    futures = []
    #f = ['tt0425413']
    for imdbid in f:
        q = hs.create_query(
            type='movie',
            search_text=True,
            use_cache=True,
            title='Sin City',
            imdbid='{0}'.format(imdbid)
        )
        futures.append(hs.submit_async(q))
    #hs.submit(q)

    while len(futures) > 0:
        for item in futures:
            if item and item.done():
                futures.remove(item)
                x = None
                try:
                    x = item.result()
                except:
                    pass
                if x:
                    for provider_item in item.result():
                        if provider_item['result']:
                            print(provider_item['result']['title'])
                        else:
                            pass
                            #print(provider_item['retries_left'], provider_item['provider'], provider_item['return_code'])
        print('item done:', item.done())

    # cache = hs._cache.get_cache_object()
    # for item in cache.values():
    #     print(item)
    hs._cache.close()
