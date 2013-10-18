#!/usr/bin/env python
# encoding: utf-8


from core.pluginhandler import PluginHandler


class ProviderHandler:
    def create_provider_data(self, **kwargs):
        kwargs['response'] = kwargs['url'] = kwargs['custom'] = None
        return kwargs
