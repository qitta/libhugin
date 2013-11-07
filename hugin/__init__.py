#!/usr/bin/env python
# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor
from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloader import DownloadQueue
from hugin.providerdata import ProviderData
from hugin.query import Query
from hugin.core.cache import Cache
import threading
import sys
import queue


class Session:
    def __init__(
        self, cache_path='/tmp', parallel_jobs=2,
        timeout_sec=5, user_agent='libhugin/1.0', use_cache='True'
    ):
        self._shutdown_event = threading.Event()
        self._config = {
            'cache_path': cache_path,
            'parallel_jobs': parallel_jobs,
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
        # categorize provider for convinience reasons
        [self._categorize(provider) for provider in self._provider]

    def create_query(self, **kwargs):
        return Query(self._query_attrs, kwargs)

    def _init_download_queue(self, query):
        if query['use_cache'] is False:
            query['use_cache'] = None
        else:
            query['use_cache'] = self._cache
        return DownloadQueue(
            num_threads=self._config['parallel_jobs'],
            timeout_sec=self._config['timeout_sec'],
            user_agent=self._config['user_agent'],
            local_cache=query['use_cache']
        )

    def submit(self, query):
        finished_jobs = []
        download_queue = self._init_download_queue(query)

        jobs = self._process_new_query(query)
        [download_queue.push(provider_data) for provider_data in jobs]

        while True:
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
        return self._async_executor.submit(
            self.submit,
            query
        )

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

if __name__ == '__main__':
    shutdown_event = threading.Event()
    try:
        hs = Session(parallel_jobs=5, timeout_sec=5)
        f = open('./hugin/core/testdata/imdbid_small.txt').read().splitlines()
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
                if item.done():
                    for provider_item in item.result():
                        if provider_item['result']:
                            pass
                            #print(provider_item['result']['title'])
                        else:
                            pass
                            #print(provider_item['retries_left'], provider_item['provider'], provider_item['return_code'])
                    futures.remove(item)
                else:
                    pass

        # cache = hs._cache.get_cache_object()
        # for item in cache.values():
        #     print(item)
        hs._cache.close()
    except (KeyboardInterrupt, SystemExit):
        shutdown_event.set()
        sys.exit(s)
