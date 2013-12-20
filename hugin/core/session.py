#!/usr/bin/env python
# encoding: utf-8

""" Session handling for hugin core module. """

# stdlib
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from itertools import zip_longest
from functools import reduce
from operator import add
import math
import types
import signal
import queue
import copy
import requests
import re

# hugin
from hugin.utils.stringcompare import string_similarity_ratio
from hugin.core.pluginhandler import PluginHandler
from hugin.core.downloadqueue import DownloadQueue
from hugin.core.provider.result import Result
from hugin.core.cache import Cache
from hugin.core.query import Query


class Session:
    """
    The hugin session is the enty point to use linhugin core.

    Example Usage:

    .. code-block:: python

        >>> getting and intializing the session
        >>> from hugin.core import Session
        >>> session = Session()
        >>>
        >>> # fetching the movie *Sin City*
        >>> query = session.create_query(title='Sin City')
        >>> results = s.submit(query)
        [<TMDBMovie <movie, picture> : Sin City (2005)>,
        <OFDBMovie <movie> : Sin City (2005)>,
        <OMDBMovie <movie> : Sin City (2005)>]

        >>> # fetching the person *Emily Browning*
        >>> q = session.create_query(name='emily browning')
        >>> result = session.submit(q)
        >>> print(result)
        [<TMDBPerson <person, picture> : Emily Browning>]


    """
    def __init__(
        self, cache_path='/tmp', parallel_jobs=2, parallel_downloads_per_job=8,
        timeout_sec=5, user_agent='libhugin/1.0'
    ):
        """
        Init a session object with user specified parameters.

        :param cache_path: Path of cache to be written to.
        :param parallel_jobs: Number of simultaneous jobs to be used.
        :param parallel_downloads_per_job: Number of simultaneous downloads.
        :param timeout_sec: Timeout for http requests to be used.

        """
        signal.signal(signal.SIGINT, self._signal_handler)
        self._config = {
            'cache_path': cache_path,
            # limit parallel jobs to 4, there is no reason for a huge number of
            # parallel jobs because of the GIL
            'parallel_jobs': min(4, parallel_jobs),
            'download_threads': parallel_downloads_per_job,
            'timeout_sec': timeout_sec,
            'user_agent': user_agent,
        }

        self._plugin_handler = PluginHandler()
        self._plugin_handler.activate_plugins_by_category('Provider')
        self._plugin_handler.activate_plugins_by_category('OutputConverter')
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
            max_workers=self._config['parallel_jobs']
        )

        self._cleanup_triggered = False
        self._provider_types = {
            'movie': [],
            'movie_picture': [],
            'person': [],
            'person_picture': []
        }
        self._downloadqueues = []
        self._submit_futures = []
        self._shutdown_session = False

        # categorize provider for convinience reasons
        for provider in self._provider:
            self._categorize(provider)

    def create_query(self, **kwargs):
        """
        Validate params and return a :class:`hugin.core.query.Query` object build from user given kwargs.

        The following parameters are possible (default value inside brackets):

        Movie specific:

        :param str title: Movie title.
        :param int year: Movie release date.
        :param str imdbid: The imdbid.

        Person specific:

        :param str name: Person name.

        General:

        :param str search: Search textual, picture or both [text].
        :param str strategy: Search strategy deep or flat [flat].
        :param bool cache: Use local cache [True].
        :param int retries: Number of retries per request [5].
        :param int amount: Number of Items yout want to get [3].
        :param list providers: A list with provider name strings [all].
        :param str language: Language `ISO 639-1 <http://en.wikipedia.org/wiki/ISO_639>`_ Format ['']
        :param bool fuzzysearch: Enable 'fuzzy search' mode.
        :param str type: Type of metadata. person, movie.

        .. note::

            All invalid key parameters will be filtered.  If there are missing
            or inconsistent values a KeyError exception will be raised by the
            Query.

        """
        return Query(kwargs)

    def _init_download_queue(self, query):
        """ Return a downloadqueue configured with user specified parameters.

        :retrun: A configured downloadqueue.

        """
        if query.cache:
            # print('enabling cache.')
            query.cache = self._cache
        else:
            query.cache = None

        if query['fuzzysearch']:
            self._fuzzy_search(query)


        downloadqueue = DownloadQueue(
            num_threads=self._config['download_threads'],
            timeout_sec=self._config['timeout_sec'],
            user_agent=self._config['user_agent'],
            local_cache=query.cache
        )
        self._downloadqueues.append(downloadqueue)
        return downloadqueue

    def _add_to_cache(self, response):
        """ Write a response tuple (url, data) to local cache. """
        for url, data in response:
            self._cache.write(url, data)

    def _submit(self, query):
        """ Here be dragons. """
        results = []
        downloadqueue = self._init_download_queue(query)

        for job in self._create_jobs_according_to_search_params(query):
            if job.done:
                results.append(self._job_to_result(job, query))
            else:
                downloadqueue.push(job)

        while True:
            try:
                job = downloadqueue.pop()
            except queue.Empty:
                break

            if not job.response:
                results.append(self._job_to_result(job, query))
                continue

            response = copy.deepcopy(job.response)
            # trigger provider to parse its request and process the result
            job.result, job.done = job.provider.parse_response(
                job.response, query
            )

            if job.result:
                self._add_to_cache(response)

            if job.done:
                results.append(self._job_to_result(job, query))
            else:
                self._process_flagged_as_not_done(
                    job, downloadqueue, query, results
                )
        downloadqueue.push(None)
        return self._select_results_by_strategy(results, query)

    def submit(self, query):
        """
        Submit a synchronous search query that blocks until finished.

        :param query: Query object with search parameters.
        :returns: A list with result objects.

        """
        if self._shutdown_session:
            self.clean_up()
        else:
            return self._submit(query)

    def submit_async(self, query):
        """ Invoke :func:`submit` asynchronously. """
        future = self._async_executor.submit(
            self.submit,
            query
        )
        self._submit_futures.append(future)
        return future

    def _process_flagged_as_not_done(self, job, downloadqueue, query, results):
        """ Process jobs which are marked as not done by provider. """
        if job.result:
            new_jobs = self._create_new_jobs_from_urls(
                job.result, job.provider, query
            )
            for job in new_jobs:
                downloadqueue.push(job)
        else:
            job = self._decrement_retries(job)
            if job.done:
                results.append(self._job_to_result(job, query))
            else:
                downloadqueue.push(job)

    def _fuzzy_search(self, query):
        if query['title'] and query['imdbid'] is None:
            fmt = 'http://www.google.com/search?hl=de&q={title}+imdb&btnI=745'
            #print(fmt.format(title=query['title']))
            url = requests.get(fmt.format(title=query['title'])).url
            imdbids = re.findall('\/tt\d*/', url)
            if imdbids:
                query['imdbid'] = imdbids.pop().strip('/')

    def _select_results_by_strategy(self, results, query):
        """
        Filter result objects according to user specified search strategy.

        :param results: A list with finished results.
        :param query: The query that belongs to the results given.

        """
        if query.remove_invalid:
            results = [result for result in results if result._result_dict]

        if len(results) == 0:
            return results

        if query.strategy == 'deep':
            return self._results_deep_strategy(results, query)
        else:
            return self._results_flat_strategy(results, query)

    def _results_deep_strategy(self, results, query):
        """ Return results proccessed with deep strategy. """
        results.sort(key=lambda x: x.provider._priority, reverse=True)
        results = self._sort_by_ratio(results, query)
        return results[:query.amount]

    def _results_flat_strategy(self, results, query):
        """ Return results proccessed with flat strategy. """
        result_map = defaultdict(list)
        # group by provider
        for result in results:
            result_map[result.provider].append(result)

        # sort by ratio
        for provider, results in result_map.items():
            result_map[provider] = self._sort_by_ratio(results, query)

        results = list(
            filter(None, reduce(add, zip_longest(*result_map.values())))
        )
        return results[:query.amount]

    def _sort_by_ratio(self, results, query):
        """ Sort results by ratio between result and search params. """
        ratio_table = []
        qry_imdb = query.get('imdbid')
        for result in filter(lambda res: res._result_dict, results):
            ratio = 0.0
            if qry_imdb and qry_imdb == result._result_dict['imdbid']:
                ratio = 1.0
            elif query.get('title'):
                ratio_a = string_similarity_ratio(
                    query.title, result._result_dict['original_title']
                )
                ratio_b = string_similarity_ratio(
                    query.title, result._result_dict['title']
                )
                ratio = max(ratio_a or 0.0, ratio_b or 0.0)
                # TODO: Fix first time wrong results. Maybe sort by year?
                if query.get('year') and result._result_dict['year']:
                    a, b = query.get('year'), result._result_dict['year']

                    penalty = math.sqrt(1 - (abs(a - b) / max(a, b)))
                    ratio *= penalty

            ratio_entry = {'result': result, 'ratio': ratio}
            ratio_table.append(ratio_entry)

        ratio_table.sort(key=lambda x: x['ratio'], reverse=True)
        return [res['result'] for res in ratio_table]

    def _job_to_result(self, job, query):
        """ Return a result generated from finished job and query. """
        retries = query.retries - job.retries_left
        result = Result(
            provider=job.provider,
            query=query,
            result=job.result,
            retries=retries
        )
        return result

    def _decrement_retries(self, job):
        """ Decrement retries inside job, set to done if no retries left. """
        if job.retries_left > 0:
            job.retries_left -= 1
        else:
            job.done = True
        return job

    def _get_job_struct(self, provider, query):
        """ Return a job structure. """
        params = [
            'url', 'future', 'response', 'done', 'result', 'return_code',
            'retries_left', 'provider'
        ]
        job = types.SimpleNamespace(**{param: None for param in params})
        job.provider, job.retries_left = provider, query.retries
        return job

    def _get_matching_provider(self, query):
        """ Return provider list with according to params in query. """
        providers = []
        for key, value in self._provider_types.items():
            if query.type in key:
                providers += self._provider_types[key]

        if query.providers:
            allowed_provider = [x.upper() for x in query.providers]
            prov_filter = lambda x: x['name'].name.upper() in allowed_provider
            providers = [x for x in filter(prov_filter, providers)]
        return providers

    def _create_jobs_according_to_search_params(self, query):
        """ Create new jobs, according to given search params in query. """
        job_list = []
        for provider in self._get_matching_provider(query):
            provider = provider['name']
            job = self._get_job_struct(provider=provider, query=query)
            url_list = job.provider.build_url(query)

            if url_list is not None:
                job.url = url_list
            else:
                job.done = True
            job_list.append(job)

        return job_list

    def _create_new_jobs_from_urls(self, urls, provider, query):
        """ Create new jobs from urls and a specific provider. """
        jobs = []
        for url_list in urls:
            job = self._get_job_struct(provider=provider, query=query)
            job.url = url_list
            jobs.append(job)
        return jobs

    def _categorize(self, provider):
        """ Cagegorizes providers according to its type. """
        self._provider_types[provider.identify_type()].append(
            {'name': provider, 'supported_attrs': provider.supported_attrs}
        )

    def postprocessing_plugins(self, pluginname=None):
        return self._get_plugin(self._postprocessing, pluginname)

    def converter_plugins(self, pluginname=None):
        """ Return converters, this is for test purposes only. """
        return self._get_plugin(self._converter, pluginname)

    def provider_plugins(self, pluginname=None):
        """ Return converters, this is for test purposes only. """
        return self._get_plugin(self._provider, pluginname)

    def _get_plugin(self, plugins, pluginname=None):
        if pluginname is None:
            return plugins
        else:
            for plugin in plugins:
                if pluginname.upper() in plugin.name.upper():
                    return plugin

    def clean_up(self):
        """ Do a clean up on keyboard interrupt or submit cancel. """
        if self._cleanup_triggered is False:
            self._cleanup_triggered = True
            print('You pressed Ctrl+C!')
            print('cleaning  up.')
            # kill all pending futures
            for future in self._submit_futures:
                if future.running() is False and future.done() is False:
                    future.cancel()
            print('waiting for remaining futures to complete.')
            self._async_executor.shutdown(wait=True)
            # print('closing cache.')
            self._cache.close()
            # print('cache closed.')

    def cancel(self):
        """ Cancel the currently running session. """
        self._shutdown_session = True

    def _signal_handler(self, signal, frame):
        """ Invoke cancel on signal interrupt. """
        self.cancel()
