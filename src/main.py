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
        plugins = self._plugin_manager.getPluginsOfCategory(category)
        for pluginInfo in plugins:
            self._plugin_manager.activatePluginByName(
                name=pluginInfo.name,
                category=category
            )
            self._plugin_from_category[category].append(pluginInfo)
        self._category_active[category] = True

    def deactivate_plugins_by_category(self, category):
        plugins = self._plugin_manager.getPluginsOfCategory(category)
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
    print(pm.is_activated('Provider'))
    plugins = pm.get_plugins_from_category('Provider')
    print(len(plugins))
    for plugin in plugins:
        print(plugin.search(title=None))
    pm.deactivate_plugins_by_category('Provider')
    print(pm.is_activated('Provider'))
