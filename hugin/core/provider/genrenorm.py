#!/usr/bin/env python
# encoding: utf-8

import pkgutil


class GenreNormalize:
    def __init__(self, provider_genre_file):
        self._global_genre_map = []
        self._provider_genre_map = {}
        self._init_mapping(provider_genre_file)

    def _init_mapping(self, provider_genre_file):
        try:
            # read the genrefiles inside packages
            global_genre_bytes = pkgutil.get_data(
                __package__, 'normalized_genre.dat'
            )
            provider_genre_bytes = pkgutil.get_data(
                __package__, provider_genre_file
            )

            # create the mapping according given genre files
            self._global_genre_map = self.create_global_genre_map(
                global_genre_bytes.decode('utf-8')
            )
            self._provider_genre_map = self.create_provider_genre_map(
                provider_genre_bytes.decode('utf-8')
            )
        except (UnicodeError, OSError) as e:
            print('Error while reading genrenormalization files.', e)

    def print_mapping(self):
        for idx_genre in self._provider_genre_map:
            idx, genres = idx_genre
            for genre in genres:
                genre = genre.strip()
                print(genre, '-->', self.normalize_genre(genre, 'de'))

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

    def normalize_genre(self, genre, output_lang='de'):
        for idx, provider_genre_list in self._provider_genre_map:
            for provider_genre in provider_genre_list:
                if genre.strip().upper() == provider_genre.upper():
                    idx, de, en = self._global_genre_map[int(idx)]
                    if output_lang == 'de':
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
    print('genre normalization.')
    for provider_genre in glob.glob('hugin/core/provider/*.genre'):
        print('===> ', provider_genre)
        gn = GenreNormalize(provider_file=provider_genre)
        f = open(provider_genre, 'r').read().splitlines()
        for item in f:
            idx, *genre = item.split(',')
            genres = [g.strip() for g in genre]
            for genre in genres:
                print('Provider:', genre, 'DE --> Global:', gn.normalize_genre(genre, 'de'))
                print('Provider:', genre, 'EN --> Global:', gn.normalize_genre(genre, 'en'))
        print()
