#!/usr/bin/env python
# encoding: utf-8

""" Postprocessing module to create a custom result out of found results. """

# stdlib
from collections import defaultdict
import copy

# hugin
from hugin.core.provider.result import Result
import hugin.core.provider as provider


class CustomProvider(provider.IPostprocessing):
    """Create a custom result.

    .. note::

        public methods:

            create_custom_result(resultlist)
    """

    def __init__(self):
        # attrs to be merged on auto merge
        self._mergable_attrs = ['title', 'plot']

    def create_custom_result(self, results, profile=None):
        """
        Merge results to fill gaps or create results defined by profile.

        :param results: A list with result objects.
        :param profile: A user defined profile for merging results.
        :returns: A list with custom results.
        """
        custom_results = []
        valid_results = [result for result in results if result.result_dict]
        grouped_results = self._group_by_imdbid(valid_results)
        for results in grouped_results.values():
            if len(results) > 1:
                if profile is None:
                    new_result = self._merge_results_by_priority(results)
                else:
                    new_result = self._merge_results_by_profile(
                        results, profile
                    )
                normalized_multi_genre = self._create_multi_provider_genre(
                    results, 'genre_norm'
                )
                new_result._result_dict['genre_norm'] = normalized_multi_genre
                custom_results.append(new_result)
        return custom_results

    def _create_multi_provider_genre(self, results, genre_key):
        """
        Merge genres from different provider results where movie is equal.

        :param results: Results of with genre should be merged.
        :param genre_key: Key of genre list to be merged.

        :return: A list with merged genre attribute.
        """
        multi_provider_genre = set()
        for result in results:
            for genre_list in result._result_dict[genre_key]:
                multi_provider_genre.add(genre_list)
        return multi_provider_genre

    def _create_result_copy(self, result, provider_name='result_profiler'):
        """
        Create a new result object.

        :param result: Result to be copied.
        :param provider_name: Provider to be exchanged in the new result.

        :returns: A result object with custom provider labeling.
        """
        return Result(
            provider=provider_name,
            query=result._search_params,
            result=copy.deepcopy(result._result_dict),
            retries=0
        )

    def _merge_results_by_priority(self, results):
        """
        Automerge results when no merge profile is given.

        Strategy: The highest priority provider is taken as baseresult. All
        missing attributes that are in :attribute:`_mergable_attrs`.

        :results: A list with results to be merged.

        :returns: A custom result.
        """
        results.sort(
            key=lambda result: result.provider._priority, reverse=True
        )
        high_prio_result, *left_results = results
        custom_result = self._create_result_copy(high_prio_result)
        self._try_fill_empty_fields(custom_result, left_results)
        return custom_result

    def _try_fill_empty_fields(self, new_result, left_results):
        """
        Helper to fill missing attrs.

        :param new_result: Result of which missing attrs should be filled.
        :param left_result: Results left for automatic attrs filling.

        """
        for left_result in left_results:
            for key, value in new_result._result_dict.items():
                left_result = left_result._result_dict[key]
                if key in self._mergable_attrs:
                    if not value:
                        new_result._result_dict[key] = value or left_result

    def _merge_results_by_profile(self, results, profile):
        """
        Merge results by user given merge profile.

        :results: A list with results to be merged.
        :returns: A custom result according to profile user specs.

        """
        # getting the default result provider
        for name in profile['default']:
            result_provider = self._get_result_by_providername(results, name)

        custom_result = self._create_result_copy(result_provider)

        # filling the partial stuff on the default result
        for key, provider_list in profile.items():
            if key != 'default':
                for provider_name in provider_list:
                    provider_result = self._get_result_by_providername(
                        results, provider_name
                    )._result_dict[key]

                    if provider_result:
                        custom_result._result_dict[key] = provider_result
                        break
        return custom_result

    def _get_result_by_providername(self, results, provider_name):
        """
        Find result with a specific provider name and return it.

        :param results: A list with result objects.
        :param provider_name: Name of the provider to be search for in results.
        :returns: Returns provider with given provider_name.

        """
        for result in results:
            if provider_name == result.provider.name:
                return result

    def _group_by_imdbid(self, results):
        """
        Group result list by imdbid.

        :param results: A list with results to be grouped by imdbid.
        :returns: Grouped results with imdbid as key

        """
        grouped_results = defaultdict(list)
        for result in results:
            imdbid = result._result_dict['imdbid']
            if imdbid is not None:
                grouped_results[imdbid].append(result)
        return grouped_results

    def __repr__(self):
        return 'custom result postprocessing filter.'

    def get_name(self):
        return self.name
