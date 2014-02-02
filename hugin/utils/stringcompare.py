#!/usr/bin/env python
# encoding: utf-8

""" String compare utils. """

import difflib


def string_similarity_ratio(s1, s2):
    """
    A string compare function, using the Redcliff-Obershelp algorithm. For
    further details see: http://docs.python.org/3.3/library/difflib.html
    TODO: Levenshtein might be better for this purpose.

    :params s1, s2: Two input strings which will be compared
    :returns: A ratio between 0.0 (not similar at all) and 1.0 (probably the
    same string).

    """
    s1 = _clean_movie_title(s1)
    s2 = _clean_movie_title(s2)
    if s1 and s2:
        return difflib.SequenceMatcher(None, s1.upper(), s2.upper()).ratio()


def _clean_movie_title(title):
    if title:
        word_list = title.replace(',', ' ').split()
        word_list.sort()
        clean_word_list = [w.strip() for w in word_list]
        return ' '.join(clean_word_list)


if __name__ == '__main__':
    import unittest

    class TestUtils(unittest.TestCase):

        def test_string_similarity_ratio_nonequal(self):
            # similary should be small here, lets assume its smaller than 30%
            ratio = string_similarity_ratio('katzenbaum', 'elchwald')
            self.assertTrue(ratio < 0.30)

        def test_string_similarity_ratio_equal(self):
            # same string, similarity should be near 100%
            ratio = string_similarity_ratio('katzenbaum', 'katzenbaum')
            self.assertTrue(ratio >= 1.0)

        def test_string_similarity_ratio_similar(self):
            # not exactly the same string, but similar enough to 70%
            ratio = string_similarity_ratio('katzenbaum', 'katzenwald')
            self.assertTrue(ratio >= 0.7)

    unittest.main()
