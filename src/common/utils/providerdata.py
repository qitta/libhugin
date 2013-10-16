#!/usr/bin/env python
# encoding: utf-8


def get_provider_data_object(provider, search_string, num_retries):
    return {
        'provider': provider,
        'search': search_string,
        'url': None,
        'response': None,
        'status_code': None,
        'retries': int(num_retries),
        'custom': None
    }
