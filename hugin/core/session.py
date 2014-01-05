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

    def __init__(
        self, cache_path='/tmp', parallel_jobs=1, parallel_downloads_per_job=8,
        timeout_sec=5, user_agent='libhugin/1.0'
    ):
        """
        Init a session object with user specified parameters.

        Creating a Session:

        .. code-block:: python

            # importing the session
            from hugin.core import Session
            session = Session()

        There are some Session parameters like the 'user-agent' that may be
        changed by the user. The following example will create a Session that
        uses the user agent *'ravenlib/1.0'*, the cache will be stored at
        */tmp/hugincache/*, two job threads will be used, each job will have
        four simultanous *download threds* and the timeout for each http
        response will be ten seconds.

        Example:

        .. code-block:: python

            session = Session(
                user_agent='ravenlib/1.0',
                cache_path='/tmp/hugincache',
                parallel_jobs=2,
                parallel_downloads_per_job=4,
                timeout_sec=10
            )


        The following parameters are customizable by the user:

        :param str cache_path: Path of cache to be written to.

        This is the path where the *cache container* should be saved. Currently
        the cache is a python shelve storing valid  http responses.

        :param parallel_jobs: Number of simultaneous jobs to be used.

        This parameter is used to set the number of simultaneous jobs. The
        default value is 1, as there is not much performance gain because of
        the GIL. The main purpose if of threads in this case is to make
        asynchronous submit execution possible.

        :param int parallel_downloads_per_job: Number of simultaneous downloads.

        This parameter sets the number of parallel download jobs.  Each job
        will use this number of parallel jobs.

        :param int timeout_sec: Timeout for http requests to be used.

        This timeout will be use for *every* http response.

        :param str user_agent: User-agent to be used for metadata downloading.

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
        Validate params and return a Query.

        This function returns a Query object build of the given kwargs. Keys
        are validated and default or missing values are set by the
        :class:`hugin.core.query.Query`.

        .. note::

            All invalid key parameters will be filtered.  If there are missing
            or inconsistent values a KeyError exception will be raised by the
            Query.

        The following query will search for the movie *Sin City*, the result
        amount is limited to a max number of five items. Download retries are
        set to two.


        Example code snippet:

        .. code-block:: python

            query = session.create_query(title='Sin City', amount=5, retries=2)
            # just to illustrate how a query looks like
            print(query)
            {'year': None, 'type': 'movie', 'providers': None,
            'remove_invalid': True, 'fuzzysearch': False, 'amount': 5,
            'language': '', 'imdbid': None, 'retries': 2, 'cache': True,
            'strategy': 'flat', 'search': 'both', 'title': 'Sin City'}


        You will just receive a dictionary representing the search values.
        Depending on the metadata type there are different parameters to be
        used in a query.

        The following parameters are possible (default value inside brackets):

        Movie specific:

        :param str title: Movie title.

        The movie title, this key will set the type key to 'movie'. The title
        has to be set in single quotes.

        Example:

        .. code-block:: python

            # get a query for the movie watchmen, everything is initialized
            # with default values
            query = session.create_query(title='Watchmen')
            [...]

            # building another query, movie title with whitespace
            query = session.create_query(title='Only god forgives')
            [...]

        :param int year: Movie year.

        In most cases the movie release date as 4-digit int.

        Example:

        .. code-block:: python

            # appending a release date to the query
            query = session.create_query(title='Sin City', year=2005)
            [...]


        :param str imdbid: The imdbid.

        You can also search by imdbid, like movie titles the value has to be
        quoted.

        Example:

        .. code-block:: python

            # building a query from imdbid (Drive (2011))
            query = session.create_query(imdbid='tt0780504')


        Person specific:

        :param str name: Person name.

        The name key will set the type key to 'person'. Like movie titles,
        person names has to be set into quotes.

        Example:

        .. code-block:: python

            query = session.create_query(name='Evangeline Lilly')

        General:
        This parameters may be set on movie an person queries as they are not
        specific to a single type.

        :param str search: Search textual, picture or both [text].

        This parameter will influence the search by choosing provider that are
        only able to search for textual metadata, pictures or both.

        Example:

        .. code-block:: python

            # will trigger textual and picture only provider
            query = session.create_query(title='Sin City', search='both')

        :param str strategy: Search strategy deep or flat [flat].

        When  limiting the search results to three, every provider is looking
        for three results. After all providers are finished, the max amount of
        results according to the amount limit is returned. The way results are
        composed is defined by the strategy flag.

        Example:

        .. code-block:: python

            # invoking flat search
            query = session.create_query(
                title='Sin City', strategy='flat', amount=5
            )
            [...]

            # invoking deep search
            query = session.create_query(
                title='Sin City', strategy='deep', amount=5
            )
            [...]

        The table below illustrates a provider search with a amount limited to
        five. The first provider has found four results, the second provider
        only three and the third provider only found two results.

            Exemplar result table:

            +------------------+---------------+---------------+-------------+
            | results/provider | #1 tmdb       | #2 ofdb       | #3 imdb     |
            |    priority ---> |   90          |   80          |   70        |
            +------------------+---------------+---------------+-------------+
            | highest quality  | result1 (f,d) | result1 (f,d) | result1 (f) |
            +------------------+---------------+---------------+-------------+
            | ...              | result2 (f,d) | result2 (f)   | result2     |
            +------------------+---------------+---------------+-------------+
            | ...              | result3 (d)   | result3       |             |
            +------------------+---------------+---------------+-------------+
            | ...              | result4 (d)   | result4       |             |
            +------------------+---------------+---------------+-------------+
            | lowest quality   |               | result5       |             |
            +------------------+---------------+---------------+-------------+

        After the provider results are *collected*, only five results are
        returned to the user as amount is five.

        How the results are picked depends on the strategy. Every provider has
        a priority.  Priority of 90 is the *highest priority* in this example.
        Providers with a higher priority are preferred.

        Using the 'deep' strategy, the results are sorted by provider priority
        and the first five results (marked with 'd') are taken.
        Choosing the 'flat' strategy the results are chosen by its quality.
        This means that result1 of all three providers an result2 (marked with
        'f') of the first and second provider are returned.


        :param bool cache: Use local cache [True].

        If set the local cache will be used on each query. Http responses are
        cached. If a specific url response has already been cached previously
        it will be returned from the cache. If url is not found in the cache, a
        http request will be triggered. Only *valid* responses are cached.

        :param int retries: Number of retries per request [5].

        If a http response timeout happens or a provider response is marked as
        invalid but not finished a retry will be triggered. This parameters
        limits the max possible retries.

        :param int amount: Number of Items you want to get [3].

        This parameter limits the amount of results to be returned by a submit.

        .. code-block:: python

            # this query will return a max of 2 results
            query = session.create_query(title='Sin City', amount=2)
            [...]

        :param list providers: A list with provider name strings [all].

        With the providers parameter you can limit the search to specific
        providers by giving libhugin a list with providers you want to query.

        Example:

        .. code-block:: python

            # this query will only trigger the omdbmovie and tmdbmovie
            # provider
            q = session.create_query(
                title='Sin', providers=['omdbmovie', 'tmdbmovie']
            )
            [...]

        To get the names of all available providers use the
        :meth:`Session.provider_plugins` method.

        .. code-block:: python

            providers = session.provider_plugins()
            for provider in providers:
                print(provider.name)

        Output:

        ::

            OFDBMovie
            OFDBPerson
            OMDBMovie
            TMDBPerson
            TMDBMovie

        :param str language: Language \
                `ISO 639-1 <http://en.wikipedia.org/wiki/ISO_639>`_ Format ['']

        The language you want to use for your query. Currently there is only
        the tmdb provider that is multilingual. All other providers are limited
        to a specific language e.g. English or German. The genre normalization
        is currently also limited to German/English normalization only.

        Example:

        .. code-block:: python

            # this query will return German language attributes if the movie
            # provider is multilingual, otherwise the providers default
            # language will be returned
            query = session.create_query(title='Sin City', language='de')
            [...]

        :param bool fuzzysearch: Enable 'fuzzy search' mode.

        Content providers are pretty fussy about the title or name you search
        for. Therefor there is a fuzzy search mode implemented. This mode will
        try to get the right results even if the title/person is pretty much
        misspelled.

        Looking for the movie 'Only god forgives' works pretty well if the
        title is spelled correct, but if only a single word is misspelled like
        'Only good forgives' no results will be found by the currently
        implemented providers. The libhugin fuzzy search is a simple workaround
        that is provider independent but requires a provider to be able to do a
        imdbid lookup. Enabling this mode libhugin will guess a imdbid for your
        misspelled title and query the available providers with this id. The
        downside is that currently only exact results for the guessed imdbid
        are returned. The fuzzy search will even work if you misspell the title
        like 'unly gut forgivs'.

        Example:

        .. code-block:: python

            # searching for misspelled Sin City title, will return nothing
            query = session.create_query(title='Sun Sity')
            results = session.submit(query)
            print(result)
            []
            [...]

            # searching for misspelled Sin City title, with enabled
            # fuzzy search will return movies found by using the Sin City
            # imdbid tt0401792
            query = session.create_query(title='Sun Sity', fuzzysearch=True)
            results = session.submit(query)
            print(result)
            [<OFDBMovie <movie> : Sin City (2005)>,
            <OMDBMovie <movie> : Sin City (2005)>,
            <TMDBMovie <movie, picture> : Sin City (2005)>]
            [...]


        :param str type: Type of metadata. person, movie.

        This parameter defines the type of metadata you want to search for, it
        is currently set automatically and should be may be ignored.

        """
        return Query(kwargs)

    def _init_download_queue(self, query):
        """ Return a downloadqueue configured with user specified parameters.

        :return: A configured downloadqueue.

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

        The following code block illustrates the query usage:

        .. code-block:: python

            results = s.submit(query) # blocks
            print(result)
            [<TMDBMovie <movie, picture> : Sin City (2005)>,
            <OFDBMovie <movie> : Sin City (2005)>,
            <OMDBMovie <movie> : Sin City (2005)>]

        The :meth:`Session.submit` method blocks. You can also submit the query
        asynchronously by using the :meth:`Session.submit_async` method.

        :param query: Query object with search parameters.
        :returns: A list with result objects.

        """
        if self._shutdown_session:
            self.clean_up()
        else:
            return self._submit(query)

    def submit_async(self, query):
        """ Invoke :meth:`submit` asynchronously.

        The following code block illustrates the query usage:

        .. code-block:: python

            results_q1 = s.submit_async(query_one) # dosen't block
            results_q2 = s.submit_async(query_two) # dosen't block
            [...]

        :param query: Query object with search parameters.
        :returns: A future object objects.

        """
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

    def provider_plugins(self, pluginname=None):
        """ Return provider plugins.


        :param pluginname: Name of a specific provider.

        Passing a provider plugin name will only return a single provider.

        :returns: Provider plugin list or specific provider.

        """
        return self._get_plugin(self._provider, pluginname)

    def postprocessing_plugins(self, pluginname=None):
        """ Return postprocessing plugins.

        See analogue: :meth:`provider_plugins`
        """
        return self._get_plugin(self._postprocessing, pluginname)

    def converter_plugins(self, pluginname=None):
        """ Return converter plugins.

        See analogue: :meth:`provider_plugins`
        """
        return self._get_plugin(self._converter, pluginname)

    def _get_plugin(self, plugins, pluginname=None):
        if pluginname is None:
            return plugins
        else:
            for plugin in plugins:
                if pluginname.upper() in plugin.name.upper():
                    return plugin

    def clean_up(self):
        """ Do a clean up on keyboard interrupt or submit cancel.

        This method needs to be triggered after a cancel. It will block until
        ready.

        """
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
        """ Cancel the currently running session.

        The cancel method will set a shutdown flag inside the :meth:`Session`.
        All running jobs will be finished, pending jobs will be canceled.

        """
        self._shutdown_session = True

    def _signal_handler(self, signal, frame):
        """ Invoke cancel on signal interrupt. """
        self.cancel()
