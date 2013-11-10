#/usr/bin/env python
# encoding: utf-8

""" Responsible for loading provider, converter and prostprocessing plugins. """

from hugin.core.provider import IMovieProvider, IPictureProvider
from hugin.core.provider import IPersonProvider, IProvider
from hugin.core.provider import IOutputConverter, IPostprocessing

from yapsy.PluginManager import PluginManager


class PluginHandler:
    def __init__(self):
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
        '''
        Collects all provider, converter and prostprocessing plugins.

        '''
        self._plugin_manager.setPluginPlaces([
            'hugin/core/provider',
            'hugin/core/converter',
            'hugin/core/postprocessing'
        ])

        # setting filter categories for pluginmanager
        self._plugin_manager.setCategoriesFilter({

            # movie metadata provider
            'Provider': IProvider,

            # sub metadata provider
            'Movie': IMovieProvider,
            'Person': IPersonProvider,
            'Picture': IPictureProvider,

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
            if is_active:
                self._plugin_manager.deactivatePluginByName(
                    name=pluginInfo.name,
                    category=category
                )
                self._plugin_from_category[category].remove(pluginInfo)
            else:
                self._plugin_manager.activatePluginByName(
                    name=pluginInfo.name,
                    category=category
                )
                self._plugin_from_category[category].append(pluginInfo)
        self._category_active[category] = not is_active

    def get_plugins_from_category(self, category):
        plugins = []
        for plugin in self._plugin_from_category[category]:
            plugin.plugin_object.name = plugin.name
            plugins.append(plugin.plugin_object)
        return plugins

    def is_activated(self, category):
        return self._category_active[category]

if __name__ == '__main__':
    ph = PluginHandler()
    ph.activate_plugins_by_category('Provider')
    provider_plugins = ph.get_plugins_from_category('Provider')
    import pprint

    pprint.pprint(provider_plugins)
    for plugin in provider_plugins:
        print('Plugin is movie {0}, is picture {1}, is person {2}'.format(
            plugin.is_movie_provider,
            plugin.is_picture_provider,
            plugin.is_person_provider)
        )
    ph.deactivate_plugins_by_category('Provider')
