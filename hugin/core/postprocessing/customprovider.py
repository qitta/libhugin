#!/usr/bin/env python
# encoding: utf-8

import hugin.core.provider as provider
from collections import defaultdict
from hugin.core.provider.result import Result
import copy


class CustomProvider(provider.IPostprocessing):
    """Docstring for CustomProvider """

    def create_custom(self, result_list):
        new_result_list = []
        valid_results = self._remove_invalid_results(result_list)
        grouped_results = self._group_by_imdbid(valid_results)
        for key, results in grouped_results.items():
            if len(results) > 1:
                new_result_list.append(self._merge_results_by_priority(results))
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

    def _try_fill_empty_fields(self, new_result, left_results):
        for left_result in left_results:
            for key, value in new_result._result_dict.items():
                if key == 'genre_norm':
                    new_result._result_dict[key] = self._merge_genre(
                        new_result._result_dict[key],
                        left_result._result_dict[key]
                    )
                if value is None or value == []:
                    new_result._result_dict[key] = value or left_result._result_dict[key]

    def _merge_genre(self, genre_list_a, genre_list_b):
        return list(set(genre_list_a + genre_list_b))

    def _group_by_imdbid(self, result_list):
        grouped_results = defaultdict(list)
        for result in result_list:
            imdbid = result._result_dict['imdbid']
            if imdbid is not None:
                grouped_results[imdbid].append(result)
        return grouped_results

    def _remove_invalid_results(self, result_list):
        valid_results = []
        for result in result_list:
            if result._result_dict is not None and result._result_dict != []:
                valid_results.append(result)
        return valid_results

    def __repr__(self):
        return 'Custom Result Postprocessing'

    def get_name(self):
        return self.name
