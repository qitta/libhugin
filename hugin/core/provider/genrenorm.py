#!/usr/bin/env python
# encoding: utf-8


import os

GLOBAL_GENRE = 'hugin/core/provider/normalized_genre.dat'

class GenreNormalize:

    def __init__(self, provider_file=None):
        self._global_genre_map = []
        self._provider_genre_map = {}
        self._provider_genre_file = provider_file
        self._global_genre_file = os.path.abspath(GLOBAL_GENRE)
        self._init_mapping()

    def _init_mapping(self):
        self._global_genre_map = self.create_global_genre_map(
            self.read_genre(self._global_genre_file)
        )
        self._provider_genre_map = self.create_provider_genre_map(
            self.read_genre(self._provider_genre_file)
        )


    def print_mapping(self):
        for idx_genre in self._provider_genre_map:
            idx, genres = idx_genre
            for genre in genres:
                genre = genre.strip()
                print(genre, '-->', self.normalize_genre(genre, 'de'))


    def read_genre(self, genre_file):
        print('reading:', genre_file)
        with open(genre_file, 'r') as f:
            return f.read()

    def clean_genre_string(self, genre_list):
        cleaned = []
        for genre in genre_list:
            cleaned.append(genre.strip())
        return cleaned

    def create_global_genre_map(self, genre_list):
        genre_map = []
        for genre in genre_list.splitlines():
            num, de, en = self.clean_genre_string(genre.split(','))
            genre_map.append((num, de, en))
        return genre_map

    def create_provider_genre_map(self, genre_list):
        genre_map = []
        for genre in genre_list.splitlines():
            idx, *genre_list = genre.split(',')
            clean_genre_list = []
            for genre in genre_list:
                clean_genre_list += self.clean_genre_string(genre.split(','))
                clean_genre_list = list(set(clean_genre_list))
                item = (idx, (clean_genre_list))
            genre_map.append(item)
        return genre_map

    def normalize_genre(self, genre, lang='de'):
        for idx, *provider_genre_list in self._provider_genre_map:
            provider_genre_list = provider_genre_list.pop()
            for provider_genre in provider_genre_list:
                if genre.strip().upper() == provider_genre.upper():
                    idx, de, en = self._global_genre_map[int(idx)]
                    if lang == 'de':
                        return de.strip()
                    else:
                        return en.strip()

    def normalize_genre_list(self, genre_list, output_lang='de'):
        normalized = []
        for genre in genre_list:
            normalized_genre = (self.normalize_genre(genre, output_lang))
            if normalized_genre is not None:
                normalized.append(normalized_genre)
        return normalized

if __name__ == '__main__':
    import glob
    for provider_genre in glob.glob('*.genre'):
        print('\n', provider_genre, 20 * '==')
        gn = GenreNormalize(provider_file=provider_genre)
        f = open(provider_genre, 'r').read().splitlines()
        for item in f:
            idx, *genre = item.split(',')
            genres = [g.strip() for g in genre]
            for genre in genres:
                print(genre, '-->', gn.normalize_genre(genre, 'de'))
