#!/usr/bin/env python
# encoding: utf-8

from core.downloader import DownloadQueue
from core.pluginhandler import PluginHandler
from core.providerhandler import ProviderHandler

if __name__ == '__main__':
    pm = PluginHandler()
    print(pm.is_activated('Provider'))
    pm.activate_plugins_by_category('Provider')
    print('Provider activated:', pm.is_activated('Provider'))
    plugins = pm.get_plugins_from_category('Provider')

    from core.downloader import DownloadQueue
    import pprint
    import time
    dq = DownloadQueue()
    ph = ProviderHandler()

    for provider in plugins:
        for item in open('core/tmp/imdbid_huge.txt', 'r').read().splitlines():
            pd1 = ph.create_provider_data(
                item,
                5,
                'Movie'
            )
            pd1['provider'] = provider
            pd1['url'] = provider.search(imdbid=pd1['search'])
            pprint.pprint(pd1)
            print('...appending to download queue')
            dq.push(pd1)

    i = 0
    while True:
        try:
            result = dq.pop()
            if result:
                print('#:', i, result['response'])
                i += 1
        except LookupError as le:
            print(le)
    #pm.deactivate_plugins_by_category('Provider')
    #print('Provider activated:', pm.is_activated('Provider'))
