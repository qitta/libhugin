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
        is_active = self._category_active[category]
        for pluginInfo in plugins:
            self._plugin_manager.activatePluginByName(
                name=pluginInfo.name,
                category=category
            )
            if is_active:
                self._plugin_from_category[category].remove(pluginInfo)
            else:
                self._plugin_from_category[category].append(pluginInfo)
        self._category_active[category] = not is_active

    def get_plugins_from_category(self, category):
        return [(x.plugin_object, x.name) for x in self._plugin_from_category[category]]

    def is_activated(self, category):
        return self._category_active[category]
