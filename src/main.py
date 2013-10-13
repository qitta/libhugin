#/usr/bin/env python
# encoding: utf-8

from pprint import pprint
from core.downloader import DownloadQueue
from contextlib import contextmanager
import json
import os
import time
import requests
import pprint
import sys


class PluginManager:
    def __init__(self, title, year):
        print('PluginManager Collector created.\n')
        self._init_provider()

    def _init_provider(self):
        from yapsy.PluginManager import PluginManager
        simplePluginManager = PluginManager()
        simplePluginManager.setPluginPlaces(["core/provider"])
        simplePluginManager.collectPlugins()
        plugins = [plugin for plugin in simplePluginManager.getAllPlugins()]

        # initializing provider plugins
        for pluginInfo in plugins:
            simplePluginManager.activatePluginByName(pluginInfo.name)
            plugin = pluginInfo.plugin_object
            content = self.get_content((plugin.search_movie(self._title,
                                                            self._year)))
            pprint.pprint(content)
            simplePluginManager.deactivatePluginByName(pluginInfo.name)


if __name__ == '__main__':
    main()
