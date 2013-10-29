#!/usr/bin/env python
# encoding: utf-8


from hugin.core.pluginhandler import PluginHandler


def create_provider_data(**kwargs):
    kwargs['response'] = kwargs['url'] = kwargs['custom'] = None
    return kwargs

if __name__ == '__main__':
    import unittest
    class TestProviderUtils(unittest.TestCase):


        def test(self):
            pd = create_provider_data(
                provider='some_prov',
            )
            pd['url'] = 'http://google.de'
            print('INFO:',  pd)

    unittest.main()
