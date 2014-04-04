#!/usr/bin/env python
# encoding: utf-8

# stdlib
import os
import pickle
from collections import OrderedDict

# hugin
from hugin.analyze.movie import Movie
from hugin.analyze.pluginhandler import PluginHandler


class Session:

    def __init__(self, database, attr_mask=None):
        self._dbname = database
        self._database = self.database_open(database)
        self._mask = attr_mask

        self._plugin_handler = PluginHandler()
        self._plugin_handler.activate_plugins_by_category('Analyzer')
        self._plugin_handler.activate_plugins_by_category('Modifier')
        self._plugin_handler.activate_plugins_by_category('Comparator')

        self._modifier = self._plugin_handler.get_plugins_from_category(
            'Modifier'
        )
        self._analyzer = self._plugin_handler.get_plugins_from_category(
            'Analyzer'
        )
        self._comparator = self._plugin_handler.get_plugins_from_category(
            'Comparator'
        )

    def analyze_raw(self, plugin, attr, data):
        attributes = {attr: data}
        movie = Movie('/tmp', 'fakenfo', attributes)
        plugin.analyze(movie)
        return movie.attributes[attr]

    def modify_raw(self, plugin, attr, data):
        attributes = {attr: data}
        movie = Movie('/tmp', 'fakenfo', attributes)
        plugin.modify(movie)
        return movie.attributes[attr]

    def compare_raw(self, plugin, attr, data):
        attributes = {attr: data}
        movie = Movie('/tmp', 'fakenfo', attributes)
        plugin.compare(movie)
        return movie.attributes[attr]

    def add(self, metadata_file, helper):
        attrs_mask = {key: None for key in self._mask.keys()}
        if os.path.isdir(metadata_file):
            # there is no metadata_file, so we get the directory
            movie = Movie(metadata_file, None, attrs_mask)
        else:
            # we have a metadata_file, so we can get the directory
            helper_attrs = helper(metadata_file, self._mask)
            if helper_attrs is None:
                helper_attrs = attrs_mask
            movie = Movie(
                os.path.dirname(metadata_file), metadata_file, helper_attrs
            )
        self._database[movie.key] = movie

    def stats(self):
        return "Database: {}, Entries: {}\n".format(
            self._dbname, len(self._database.keys())
        )

    def get_database(self):
        return self._database

    def analyzer_plugins(self, pluginname=None):
        return self._get_plugin(self._analyzer, pluginname)

    def modifier_plugins(self, pluginname=None):
        return self._get_plugin(self._modifier, pluginname)

    def comparator_plugins(self, pluginname=None):
        return self._get_plugin(self._comparator, pluginname)

    def _get_plugin(self, plugins, pluginname=None):
        if pluginname is None:
            return plugins
        else:
            for plugin in plugins:
                if pluginname.upper() in plugin.name.upper():
                    return plugin

    def database_open(self, database):
        try:
            with open(self._dbname, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError as e:
            return OrderedDict()

    def database_close(self):
        with open(self._dbname, 'wb') as f:
            pickle.dump(self._database, f)
