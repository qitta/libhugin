#!/usr/bin/env python
# encoding: utf-8

# stdlib
import json

# hugin
import hugin.core.provider as provider


class Json(provider.IOutputConverter):

    def convert(self, results):
        return [
            json.dumps(
                j._result_dict, sort_keys=True
            ) for j in results if j._result_dict
        ]
