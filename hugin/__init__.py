#!/usr/bin/env python
# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor
from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloader import DownloadQueue
from hugin.providerdata import ProviderData
from hugin.query import Query
import queue


class Session:
    def __init__(self, cache_path='/tmp', parallel_jobs=10, timeout_sec=3.0):
        self._config = {
            'cache_path': cache_path,
            'parallel_jobs:': parallel_jobs,
            'timeout_sec': timeout_sec,
            'profile': {
                'default': [],
                'search_pictures': False,
                'search_text': True
            }
        }
        self._query_attrs = [
            'title', 'year', 'name', 'imdbid', 'type', 'search_text',
            'language', 'seach_picture', 'items'
        ]
        self._plugin_handler = PluginHandler()
        self._plugin_handler.activate_plugins_by_category('Provider')
        self._downloadqueue = DownloadQueue()
        self._jobhandler = JobHandler(self._downloadqueue)
        self._provider = self._plugin_handler.get_plugins_from_category(
            'Provider'
        )
        self._async_executor = ThreadPoolExecutor(max_workers=20)

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

    def submit(self, query):
        finished_jobs = []
        active_jobs = self._process_new_query(query)

        for provider_data in active_jobs:
            self._downloadqueue.push(provider_data)

        while len(active_jobs) > 0:
            print(len(active_jobs))
            try:
                provider_data = self._downloadqueue.pop()
                if provider_data.query is query:
                    provider_data.parse()
                    if provider_data.is_done:
                        finished_jobs.append(provider_data)
                        active_jobs.remove(provider_data)
                    else:
                        finished, new = self._process(provider_data)
                        for provider_data in finished:
                            active_jobs.remove(provider_data)
                            finished_jobs.append(provider_data)

                        for provider_data in new:
                            if provider_data not in active_jobs:
                                active_jobs.append(provider_data)
                            self._downloadqueue.push(provider_data)
                else:
                    self._downloadqueue.requeue(provider_data)
            except queue.Empty:
                pass
        return finished_jobs

    def _process_new_query(self, query):
        providers = self._provider_types[query['type']]
        provider_data_list = []
        for provider in providers:
            provider_data = ProviderData(provider=provider, query=query)
            provider_data.search()
            provider_data_list.append(provider_data)
        return provider_data_list

    def _process(self, provider_data):
        new_jobs = []
        finished_jobs = []

        if provider_data.is_done:
            finished_jobs.append(provider_data)
        else:
            if provider_data.has_valid_result:
                for url in provider_data['result']:
                    provider_data = ProviderData(
                        provider=provider_data['provider'],
                        url=url,
                        query=provider_data['query']
                    )
                    new_jobs.append(provider_data)
            else:
                if provider_data.retries_left:
                    provider_data.dec_retries
                    new_jobs.append(provider_data)
                else:
                    finished_jobs.append(provider_data)
        return (finished_jobs, new_jobs)

    def submit_async(self, query):
        return self._async_executor.submit(
            self.submit,
            query
        )

    def _build_default_profile(self):
        pass

    def providers_list(self):
        return self._provider_types

    def _categorize(self, provider):
        if provider.is_picture_provider:
            self._append_picture_provider(provider)
        else:
            self._append_text_provider(provider)

    def _append_picture_provider(self, provider):
        if provider.is_movie_provider:
            self._provider_types['movie_picture'].append(provider)
        else:
            self._provider_types['person_picture'].append(provider)

    def _append_text_provider(self, provider):
        if provider.is_movie_provider:
            self._provider_types['movie'].append(provider)
        else:
            self._provider_types['person'].append(provider)

    def converter_list(self):
        pass

    def config_list(self):
        return self._config

    def profile_list(self):
        pass

    def profile_add(self):
        pass

    def profile_remove(self):
        pass


if __name__ == '__main__':
    hs = Session(timeout_sec=15)
    # f = open('./hugin/core/testdata/imdbid_small.txt').read().splitlines()
    futures = []
    # f = ['tt0425413']
    # for imdbid in f:
    q = hs.create_query(
        title='sin city',
        year='',
        name='emma stone',
        type='movie',
        search_text=True,
        items=1
    )
    print(hs.submit(q))

    # while len(futures) > 0:
    #     for item in futures:
    #         if item.done():
    #             print(item.result())
    #             futures.remove(item)
    #         else:
    #             pass

    #full = len(futures)
    #while len(futures) > 0:
    #    for item in futures:
    #        if item.done():
    #            print(item.result())
    #            futures.remove(item)
    #        else:
    #            pass
    #print(len(futures))
    #print(full)
