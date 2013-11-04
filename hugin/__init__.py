#!/usr/bin/env python
# encoding: utf-8

from collections import UserDict
from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloader import DownloadQueue
import queue


class Session:
    def __init__(self, cache_path='/tmp', parallel_jobs=20, timeout_sec=3.0):
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

    def _build_default_profile(self):
        pass

    def submit(self, query):
        self._process_new_query(query)
        while True:
            try:
                pd = self._downloadqueue.pop()
                pd.parse()
                if pd.is_done:
                    print(pd['provider'], pd['result'], pd['retries'])
                else:
                    self._process(pd)
            except queue.Empty as e:
                return

    def _process_new_query(self, query):
        provider = self._provider_types['movie']
        for item in provider:
            pd = ProviderData(provider=item, query=query)
            pd.search()
            self._downloadqueue.push(pd)

    def _process(self, pd):
        if pd['retries'] == 0:
            pd['done'] = True
        elif pd['result'] is None:
            self._downloadqueue.push(pd)
        else:
            for url in pd['result']:
                provider_data = ProviderData(provider=pd['provider'], url=url, query=pd['query'])
                self._downloadqueue.push(provider_data)



    def submit_async(self, query):
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


class ProviderData(UserDict):
    def __init__(self, url=None, provider=None, query=None):
        self.data = {
            'url': url,
            'provider': provider,
            'query': query,
            'response': None,
            'done': False,
            'result': None,
            'retries': 50
        }

    def search(self):
        self['url'] = self['provider'].search(self['query'])
        self['done'] = True

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
    q = hs.create_query(
        title='django unchained', # make tmdb search bei imdbid
        # http://api.themoviedb.org/3/movie/tt0105236?api_key=###
        year='',
        type='movie',
        imdbid='tt0401792',
        search_text=True,
    )
    hs.submit(q)
