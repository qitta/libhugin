#!/usr/bin/env python
# encoding: utf-8

from hugin.core.downloader import DownloadQueue
from hugin.core.pluginhandler import PluginHandler
from hugin.core.providerhandler import ProviderHandler

if __name__ == '__main__':
    pm = PluginHandler()
    print(pm.is_activated('Provider'))
    pm.activate_plugins_by_category('Provider')
    print('Provider activated:', pm.is_activated('Provider'))
    provider_plugins = pm.get_plugins_from_category('Provider')

    from hugin.core.downloader import DownloadQueue
    import pprint
    import time
    download_queue = DownloadQueue()
    provider_handler = ProviderHandler()
    movies = ['Sin City']
    params = {'title': 'Watchmen', 'year': 2005, 'imdbid': None, 'items': 4}

    for provider in provider_plugins:
        for movie_title in movies:
            provider_item, name = provider
            if 'OFDB' in name.upper():
                pd1 = provider_handler.create_provider_data(
                    provider=provider_item,
                    search_params=params
                )
                pd1['provider'] = provider_item
                pd1['url'] = provider_item.search(params)
                download_queue.push(pd1)

    while True:
        try:
            provider_data = download_queue.pop()
            print('POPPED PROVIDERDATA:', provider_data)
            provider = provider_data.get('provider')
            print('PROVIDER', provider)
            response = provider_data.get('response')
            if response:
                result = provider.parse(
                    response,
                    params
                )
                if isinstance(result, list):
                    for url in result:
                        pd = provider_handler.create_provider_data(
                            provider=provider_data.get('provider'),
                            search_params=provider_data.get('params')
                        )
                        print('PROVIDERDATA NEW:', pd)
                        download_queue.push(pd)
                else:
                    print('no parse feedback')
        except LookupError as le:
            print('EXCEPTION:', le)


    #pm.deactivate_plugins_by_category('Provider')
    #print('Provider activated:', pm.is_activated('Provider'))
