#/usr/bin/env python
# encoding: utf-8

from yapsy.PluginManager import PluginManager
from core.downloader import DownloadQueue
from core.provider import *


class PluginHandler:
    def __init__(self):
        print('PluginManager Collector created.\n')
        self._plugin_manager = PluginManager()
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
        for pluginInfo in self._plugin_manager.getPluginsOfCategory(
            category
        ):
            self._plugin_manager.activatePluginByName(
                name=pluginInfo.name,
                category=category
            )

    def deactivate_plugins_by_category(self, category):
        for pluginInfo in self._plugin_manager.getPluginsOfCategory(
            category
        ):
            self._plugin_manager.deactivatePluginByName(
                name=pluginInfo.name,
                category=category
            )

    def get_provider_plugins(self):
        return [x.plugin_object for x in self._provider_plugins]

    def get_converter_plugins(self):
        return [x.plugin_object for x in self._converter_plugins]

    def get_postprocessing_plugins(self):
        return [x.plugin_object for x in self._postprocessing_plugins]


if __name__ == '__main__':
    pm = PluginHandler()
    pm.activate_plugins_by_category('Provider')
    pm.deactivate_plugins_by_category('Provider')
