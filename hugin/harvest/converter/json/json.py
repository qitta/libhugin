#!/usr/bin/env python
# encoding: utf-8

# stdlib
import json

# hugin
import hugin.harvest.provider as provider


class Json(provider.IConverter):

    def __init__(self):
        self.file_ext = '.json'

    def convert(self, result):
        return json.dumps(result._result_dict, sort_keys=True)
