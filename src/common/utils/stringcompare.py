#!/usr/bin/env python
# encoding: utf-8

import difflib


def string_similarity_ratio(s1, s2):
    return difflib.SequenceMatcher(None, s1.upper(), s2.upper()).ratio()

if __name__ == '__main__':
    from core.providerhandler import create_provider_data
    import unittest

    class TestUtils(unittest.TestCase):

        def setUp(self):
            pass

        def test_string_similarity_ratio(self):
            string_similarity_ratio('Hello', 'Hola')

    unittest.main()
