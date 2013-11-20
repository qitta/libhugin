#!/usr/bin/env python
# encoding: utf-8

import hugin.core.provider as provider


class CustomProvider(provider.IPostprocessing):
    """Docstring for CustomProvider """

    def __init__(self):
        """@todo: to be defined """
        self._custom_map = None

    def create_custom(self, result):
        pass

    def __repr__(self):
        return 'Custom Result Postprocessing'
