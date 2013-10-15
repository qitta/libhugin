#/usr/bin/env python
# encoding: utf-8

from yapsy.PluginManager import PluginManager
from core.provider import *


class PluginHandler:
    def __init__(self):
        print('PluginManager Collector created.\n')
        self._plugin_manager = PluginManager()
        self._category_active = {
            'Provider': False,
            'OutputConverter': False,
            'Postprocessing': False
        }
        self._plugin_from_category = {
            'Provider': [],
            'OutputConverter': [],
            'Postprocessing': []
        }
        self._provider_plugins = []
        self._converter_plugins = []
        self._postprocessing_plugins = []
        self._collect_all_plugins()

    def _collect_all_plugins(self):
        self._plugin_manager.setPluginPlaces([
            'core/provider',
            'core/converter',
            'core/postprocessing'
        ])

        # setting filter categories for pluginmanager
        self._plugin_manager.setCategoriesFilter({

            # movie metadata provider
            'Provider': IProvider,

            # sub metadata provider
            'Movie': IMovieProvider,
            'Poster': IPosterProvider,
            'Backdrop': IBackdropProvider,
            'Plot': IPlotProvider,
            'Person': IPersonProvider,

            # output converter
            'OutputConverter': IOutputConverter,

            # postprocessing filter
            'Postprocessing': IPostprocessing
        })
        self._plugin_manager.collectPlugins()

    def activate_plugins_by_category(self, category):
        self._toggle_activate_plugins_by_categroy(category)

    def deactivate_plugins_by_category(self, category):
        self._toggle_activate_plugins_by_categroy(category)

    def _toggle_activate_plugins_by_categroy(self, category):
        plugins = self._plugin_manager.getPluginsOfCategory(category)
        if self._category_active[category] is False:
            for pluginInfo in plugins:
                self._plugin_manager.activatePluginByName(
                    name=pluginInfo.name,
                    category=category
                )
                self._plugin_from_category[category].append(pluginInfo)
            self._category_active[category] = True
        else:
            for pluginInfo in plugins:
                self._plugin_manager.deactivatePluginByName(
                    name=pluginInfo.name,
                    category=category
                )
                self._plugin_from_category[category].remove(pluginInfo)
            self._category_active[category] = False

    def get_plugins_from_category(self, category):
        return [x.plugin_object for x in self._plugin_from_category[category]]

    def is_activated(self, category):
        return self._category_active[category]


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
    for plugin in plugins:
        dq.push(plugin.search(imdbid='tt1034302'))
        dq.push(plugin.search(imdbid='tt2230342'))

    while True:
        time.sleep(0.5)
        try:
            result = dq.pop()
            if result and result.status_code == 200:
                pprint.pprint(result.json())
        except LookupError as le:
            print(le)

    pm.deactivate_plugins_by_category('Provider')
    print('Provider activated:', pm.is_activated('Provider'))
