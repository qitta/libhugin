#!/usr/bin/env python
# encoding: utf-8

from collections import defaultdict
from hugin.core.provider.result import Result
import hugin.core.provider as provider
import copy


class CustomProvider(provider.IPostprocessing):
    """Docstring for CustomProvider """

    def __init__(self):
        self._mergable_attrs = ['title', 'genre_norm', 'plot']
        self._merge_map = {'default': ['TMDB'], 'plot': ['OFDB', 'OMDB']}

    def create_custom(self, result_list, profile=None):
        new_result_list = []
        valid_results = self._remove_invalid_results(result_list)
        grouped_results = self._group_by_imdbid(valid_results)
        for results in grouped_results.values():
            if len(results) > 1:
                if profile is None:
                    new_result_list.append(self._merge_results_by_priority(results))
                    self._merge_results_by_profile(results, self._merge_map)
                else:
                    new_result_list.append(self._merge_results_by_profile(results, profile))
        return new_result_list

    def _merge_results_by_priority(self, results):
        results.sort(
            key=lambda result: result.provider._priority, reverse=True
        )
        high_prio_result, *left_results = results
        result_dict_copy = copy.deepcopy(high_prio_result._result_dict)
        result = Result(
            provider='result_profiler',
            query=high_prio_result._search_params,
            result=result_dict_copy,
            retries=0
        )
        self._try_fill_empty_fields(result, left_results)
        return result

    def _merge_results_by_profile(self, results, profile):
        for name in profile['default']:
            result_provider = self._get_result_by_providername(results, name)
        for key, value in profile.items():
            if key != 'default':
                pass

    def _try_fill_empty_fields(self, new_result, left_results):
        for left_result in left_results:
            for key, value in new_result._result_dict.items():
                if key in self._mergable_attrs:
                    if key == 'genre_norm':
                        new_result._result_dict[key] = self._merge_genre(
                            new_result._result_dict[key],
                            left_result._result_dict[key]
                        )
                    elif value is None or value == []:
                        new_result._result_dict[key] = value or left_result._result_dict[key]

    def _get_result_by_providername(self, results, name):
        for result in results:
            if name == result.provider.name:
                return result

    def _merge_genre(self, genre_list_a, genre_list_b):
        return set(genre_list_a) | set(genre_list_b)

    def _group_by_imdbid(self, result_list):
        grouped_results = defaultdict(list)
        for result in result_list:
            imdbid = result._result_dict['imdbid']
            if imdbid is not None:
                grouped_results[imdbid].append(result)
        return grouped_results

    def _remove_invalid_results(self, result_list):
        valid_results = filter(self._is_valid_result_dict, result_list)
        return  filter(self._is_valid_imdbid, valid_results)

    def _is_valid_result_dict(self, result):
        return result._result_dict and result._result_dict != []

    def _is_valid_imdbid(self, result):
        return isinstance(result._result_dict['imdbid'], str)

    def __repr__(self):
        return 'Custom Result Postprocessing'

    def get_name(self):
        return self.name
