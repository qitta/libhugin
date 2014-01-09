#!/usr/bin/env python
# encoding: utf-8

import os
import pickle
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

        self._modifier = self._plugin_handler.get_plugins_from_category(
            'Modifier'
        )
        self._analyzer = self._plugin_handler.get_plugins_from_category(
            'Analyzer'
        )

    def add(self, nfofile, helper):
        attrs_mask = {key: None for key in self._mask.keys()}
        if os.path.isdir(nfofile):
            # there is no nfofile, so we get the directory
            movie = Movie(nfofile, None, attrs_mask)
        else:
            # we have a nfofile, so we can get the directory
            helper_attrs = helper(nfofile, self._mask)
            if helper_attrs is None:
                helper_attrs = attrs_mask
            movie = Movie(os.path.dirname(nfofile), nfofile, helper_attrs)
        self._database[movie.key] = movie

    def stats(self):
        return "Databse: {}, Entries: {}\n".format(
            self._dbname, len(self._database.keys())
        )

    def get_database(self):
        return self._database

    def analyzer_plugins(self, pluginname=None):
        return self._get_plugin(self._analyzer, pluginname)

    def modifier_plugins(self, pluginname=None):
        return self._get_plugin(self._modifier, pluginname)

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
            return dict()

    def database_shutdown(self):
        with open(self._dbname, 'wb') as f:
            pickle.dump(self._database, f)