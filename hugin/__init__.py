#!/usr/bin/env python
# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor
from collections import UserDict
from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloader import DownloadQueue
import queue


class Session:
    def __init__(self, cache_path='/tmp', parallel_jobs=100, timeout_sec=3.0):
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
        self._provider = self._plugin_handler.get_plugins_from_category(
            'Provider'
        )
        self._async_executor = ThreadPoolExecutor(max_workers=10)

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
        jobs = []
        self._process_new_query(query)
        while True:
            try:
                provider_data = self._downloadqueue.pop()
                print('PROVIDERDATA', provider_data)
                if provider_data['job_id'] != id(query):
                    self._downloadqueue.requeue(provider_data)
                else:
                    print(provider_data)
                    provider_data.parse()
                    if provider_data.is_done:
                        jobs.append(provider_data)
                    else:
                        self._process(provider_data)
            except queue.Empty:
                return jobs
            return jobs

    def _process_new_query(self, query):
        provider = self._provider_types[query['type']]
        for item in provider:
            provider_data = ProviderData(provider=item, query=query)
            provider_data.search()
            self._downloadqueue.push(provider_data)

    def _process(self, provider_data):
        if provider_data['retries'] == 0:
            provider_data['done'] = True
        elif provider_data['result'] is None:
            self._downloadqueue.push(provider_data)
        else:
            for url in provider_data['result']:
                provider_data = ProviderData(
                    provider=provider_data['provider'],
                    url=url,
                    query=provider_data['query']
                )
                self._downloadqueue.push(provider_data)

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


# Simple query object to initialize defaults
class Query(UserDict):
    def __init__(self, query_attrs, data):
        self._query_attrs = query_attrs
        self.data = {k: None for k in self._query_attrs}
        self._set_query_values(data)

    def _set_query_values(self, data):
        for key, value in data.items():
            self.data[key] = value
        if self.data['items'] is None:
            self.data['items'] = 1


# Provider data encapsulation for simpler handling
class ProviderData(UserDict):
    def __init__(self, url=None, provider=None, query=None):
        self.data = {
            'url': url,
            'provider': provider,
            'query': query,
            'response': None,
            'done': False,
            'result': None,
            'retries': 50,
            'job_id': id(query)
        }

    def search(self):
        self['url'] = self['provider'].search(self['query'])

    def parse(self):
        provider, query = self['provider'], self['query']
        self['result'], self['done'] = provider.parse(self['response'], query)
        if self['result'] is None:
            self['retries'] -= 1
        if self['retries'] == 0:
            self['done'] = True

    def __repr__(self):
        return 'Provider:' + str(self['provider']) + str(self['result'])

    @property
    def is_done(self):
        return self['done']


if __name__ == '__main__':
    hs = Session(timeout_sec=15)
    #f = open('./hugin/core/testdata/imdbid_small.txt').read().splitlines()
    #futures = []
    #for imdbid in f:
    q = hs.create_query(
        title='Sin City',
        name='Emma Stone',
        year='',
        type='person',
        search_text=True,
        items=5
    )
    print(hs.submit(q))
    #print(id(q))
    #futures.append(hs.submit(q))

    #for item in futures:
    #    print(item)
    # full = len(futures)
    # while len(futures) > 0:
    #     for item in futures:
    #         if item.done():
    #             print(item.result())
    #             futures.remove(item)
    #         else:
    #             pass
    # print(len(futures))
    # print(full)
