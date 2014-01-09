
#/usr/bin/env python
# encoding: utf-8

""" Management module for provider, converter and prostprocessing plugins. """

# 3rd pary
from yapsy.PluginManager import PluginManager

# hugin
from hugin.analyze import IAnalyzer, IModifier


class PluginHandler:

    def __init__(self):
        self._plugin_manager = PluginManager()
        self._category_active = {
            'Modifier': False,
            'Analyzer': False
        }
        self._plugin_from_category = {
            'Modifier': [],
            'Analyzer': []
        }
        self._modifier_plugins = []
        self._analyzer_plugins = []
        self._collect_all_plugins()

    def _collect_all_plugins(self):
        self._plugin_manager.setPluginPlaces([
            'hugin/analyze/modifier',
            'hugin/analyze/analyzer'
        ])

        # setting filter categories for pluginmanager
        self._plugin_manager.setCategoriesFilter({

            # movie metadata provider
            'Modifier': IModifier,

            # sub metadata provider
            'Analyzer': IAnalyzer
        })
        self._plugin_manager.collectPlugins()

    def activate_plugins_by_category(self, category):
        self._toggle_activate_plugins_by_category(category)

    def deactivate_plugins_by_category(self, category):
        self._toggle_activate_plugins_by_category(category)

    def _toggle_activate_plugins_by_category(self, category):
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
            plugin.plugin_object.description = plugin.description
            plugins.append(plugin.plugin_object)
        return plugins

    def is_activated(self, category):
        """ True if category is activated. """
        return self._category_active[category]
