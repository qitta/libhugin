#!/usr/bin/env python
# encoding: utf-8

""" Postprocessor module to create a custom result out of found results. """

# stdlib
from collections import defaultdict
import difflib
import math
import copy

# hugin
from hugin.harvest.provider.result import Result
import hugin.harvest.provider as provider


class Composer(provider.IPostprocessor):
    """Create a custom result.

    .. autosummary::

        create_custom_result

    """

    def __init__(self):
        # attrs to be merged on auto merge
        self._mergable_attrs = ['title', 'plot', 'genre', 'genre_norm']
        self._keys = [
            'title', 'original_title', 'plot', 'runtime', 'imdbid',
            'vote_count', 'rating', 'providerid', 'alternative_titles',
            'directors', 'writers', 'crew', 'year', 'poster', 'fanart',
            'countries', 'genre', 'genre_norm', 'collection', 'studios',
            'trailers', 'actors', 'keywords', 'tagline', 'outline'
        ]

    def process(self, results, profile=None, merge_genre=True):
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
            if profile is None:
                new_result = self._merge_results_by_priority(results)
            else:
                new_result = self._merge_results_by_profile(
                    results, profile
                )
                if new_result == []:
                    continue

            normalized_multi_genre = self._create_multi_provider_genre(
                results, 'genre_norm'
            )
            if merge_genre:
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
            if result._result_dict.get(genre_key):
                for genre_list in result._result_dict[genre_key]:
                    multi_provider_genre.add(genre_list)
        return multi_provider_genre

    def _create_result_copy(self, result, provider_name='Composer'):
        """
        Create a new result object.

        :param result: Result to be copied.
        :param provider_name: Provider to be exchanged in the new result.

        :returns: A result object with custom provider labeling.
        """
        result_dict = {key:None for key in self._keys}
        result_dict.update(result.result_dict)
        return Result(
            provider=provider_name,
            query=result._search_params,
            result=result_dict,
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
        for result in left_results:
            for key, value in new_result._result_dict.items():
                if not result._result_dict.get(key):
                    continue
                left_result = result._result_dict[key]
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
            if result_provider:
                break

        if result_provider is None:
            return []

        custom_result = self._create_result_copy(result_provider)

        # filling the partial stuff on the default result
        for key, provider_list in profile.items():
            if key != 'default':
                for provider_name in provider_list:
                    provider_result = self._get_result_by_providername(
                        results, provider_name
                    )
                    if provider_result is None:
                        break
                    provider_result = provider_result._result_dict[key]

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
            if provider_name.upper() == result.provider.name.upper():
                return result

    def _group_by_imdbid(self, results):
        """
        Group result list by imdbid.

        :param results: A list with results to be grouped by imdbid.
        :returns: Grouped results with imdbid as key

        """
        no_imdbid = []
        grouped_results = defaultdict(list)
        for result in results:
            imdbid = result._result_dict.get('imdbid')
            if imdbid is not None:
                grouped_results[imdbid].append(result)
            else:
                no_imdbid.append(result)
        self._try_set_imdbid(grouped_results, no_imdbid)
        return grouped_results

    def _try_set_imdbid(self, grouped_results, no_imdbid_results):
        sanitized_groups = []
        for imdbid, result_list in grouped_results.items():
            for id_result in result_list:
                for noid_result in no_imdbid_results:
                    if self._movie_similarity(id_result, noid_result):
                        noid_result._result_dict['imdbid'] = imdbid
                        sanitized_groups.append(noid_result)
                        #result_list.pop(result_list.index(noid_result))
        for movie in sanitized_groups:
            grouped_results[movie._result_dict['imdbid']].append(movie)

        import pprint
        pprint.pprint(grouped_results)

    def _movie_similarity(self, r1, r2):
        titile_sim = self._compare_movie_title(
            r1._result_dict['title'], r2._result_dict['title']
        )
        year_sim = self._compare_movie_year(
            r1._result_dict['year'], r2._result_dict['year']
        )
        director_sim = self._cmp_director_list(
            r1._result_dict['directors'], r2._result_dict['directors']
        )
        return ((titile_sim + year_sim + director_sim) / 3) >= 0.85

    def _cmp_director_list(self, s1, s2):
        if not s1 or not s2:
            return 0.0

        s1 = [' '.join(sorted(s.split())) for s in s1]
        s2 = [' '.join(sorted(s.split())) for s in s2]

        s1, s2 = sorted([s1, s2], key=len)
        sim_sum = 0

        for director in s2:
            sim_sum += max([self.cmp_string(director, other) for other in s1])
        return (sim_sum / len(s2))


    def cmp_string(self, s1, s2):
        return difflib.SequenceMatcher(None, s1.upper(), s2.upper()).ratio()

    def _compare_movie_title(self, t1, t2):
        if t1 and t2:
            s1, s2 = self._clean_string(t1), self._clean_string(t2)
            return difflib.SequenceMatcher(None, s1.upper(), s2.upper()).ratio()

    def _clean_string(self, s):
        sorted_str = sorted(' '.join(s.split(',')).split())
        return ' '.join([x.strip() for x in sorted_str])

    def _compare_movie_year(self, y1, y2):
        if y1 and y2:
            diff = abs(abs(y1) - abs(y2)) / 3
            if diff >= 1.0:
                return 0.0
            else:
                return math.sqrt(1 - diff)
        return 0.0

    def parameters(self):
        return {
            'profile': dict,
            'merge_genre': bool
        }
