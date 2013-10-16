#!/usr/bin/env python
# encoding: utf-8


from core.pluginhandler import PluginHandler


class ProviderHandler:
    def create_provider_data(self,
                             search_string,
                             num_retries,
                             providertype):

        return {
            'provider': None,
            'type': providertype,
            'search': search_string,
            'url': None,
            'response': None,
            'status_code': None,
            'retries': int(num_retries),
            'custom': None
        }


if __name__ == '__main__':
    plugin_handler = PluginHandler()
    pd = ProviderHandler()
    provider_dict = pd.create_provider_data('TMDB', 'Sin City', 5, 'Movie')
    print(provider_dict)
