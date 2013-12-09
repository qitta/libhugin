#!/usr/bin/env python
# encoding: utf-8

""" Genre normalization module. """

import pkgutil
import os


class GenreNormalize:
    """
    Normalize genre according to given provider genre mapping files.

    ..autosummary ::

        normalize_genre
        normalize_genre_list

    """
    def __init__(self, provider_genre_file):
        """
        Create a genrenormalize object for a specific provider.

        The provider genre file naming should be 'providername.genre'. The
        mapping is done according to the genres indexes in the
        normalize_genre.dat file.

        How it works:

        Global genre mapping file (normalized_genre.dat) content snippet:

            0, Abenteuer, Adventure
            1, Action, Action
            2, Amateur, Amateur
            3, Animation, Animation
            4, Biographie, Biography
            5, Dokumentarfilm, Documentary
            6, Drama, Drama
            7, Eastern, Eastern
            8, Erotik, Erotic
            9, Essayfilm, Essayfilm
            10, Experimentalfilm, Experimental
            11, Familienfilm, Family

        A provider genre mapping file (e.g. omdb.genre) content snippet:

            0, Adventure
            11, Family
            5, Documentary
            6, Drama

        To normalize the provider genre GenreNormalize uses the probider
        mapping file. The index in the provider file before the genre is the
        index of a global genre to which the provider genre should be mapped.

        In our example the provider genres are mapped like:

            provider: 'Adventure' ==> global: 'Abenteuer, Adventure'
            provider: 'Family' ==> global: 'Familienfilm, Family'
            provider: 'Documentary' ==> global: 'Dokumentarfilm, Documentary'
            provider: 'Drama' ==> global: 'Drama, Drama'

        Whether Abenteuer or Advanture is defined by the language flag the
        normalize method supports. Currently only normalization to english and
        german is supported.

        :param provider_genre_file: Filename of provider genere mapping file.

        """
        self._global_genre_map = []
        self._provider_genre_map = {}
        self._init_mapping(provider_genre_file)

    def _init_mapping(self, provider_genre_file):
        """ Initializes mapping structures. """
        try:
            # read the genrefiles inside packages
            global_genre_bytes = pkgutil.get_data(
                __package__, os.path.join('genrefiles', 'normalized_genre.dat')
            )
            provider_genre_bytes = pkgutil.get_data(
                __package__, os.path.join('genrefiles', provider_genre_file)
            )

            # create the mapping according given genre files
            self._global_genre_map = self._create_global_genre_map(
                global_genre_bytes.decode('utf-8')
            )
            self._provider_genre_map = self._create_provider_genre_map(
                provider_genre_bytes.decode('utf-8')
            )
        except (UnicodeError, OSError) as e:
            print('Error while reading genrenormalization files.', e)

    def _print_mapping(self, provider_genre_file):
        """ Print current mapping - for test purposes only. """
        print(provider_genre_file)
        for idx_genre in self._provider_genre_map:
            idx, genres = idx_genre
            for genre in genres:
                print('Provider: {0} --> global DE: {1}.'.format(
                    genre, self.normalize_genre(genre, 'de'))
                )
                print('Provider: {0} --> global EN: {1}.'.format(
                    genre, self.normalize_genre(genre, 'en'))
                )
        print()

    def _strip_genre_list(self, genre_list):
        """ Strip genre string. """
        return [genre.strip() for genre in genre_list]

    def _create_global_genre_map(self, genre_filerepr):
        """
        Create a global genre mapping.

        Genre mapping is created out of genres listened in
        normalized_genre.dat. Genre map is a list of tuples containing the
        genre

            (index, german genre name, english genre name)

        :param genre_filerepr: A string representing the genre file
        :returns: A list containing genre index, de, en tuple.

        """
        genre_map = []
        for line in genre_filerepr.splitlines():
            num, de, en = self._strip_genre_list(line.split(','))
            genre_map.append((num, de, en))
        return genre_map

    def _create_provider_genre_map(self, genre_filerepr):
        """
        Create a provider specific genre mapping.

        This function is the counterpart to :func:`_create_global_genre_map`.

        """
        genre_map = []
        for line in genre_filerepr.splitlines():
            idx, *genres = line.split(',')
            clean_genres = list(set(self._strip_genre_list(genres)))
            genre_map.append((idx, clean_genres))
        return genre_map

    def normalize_genre(self, genre, output_lang='de'):
        """
        Normalize a given provider genre to global genre.

        :param genre: Provider specific genre.
        :param output_lang: Normalized genre output language.

        :returns: Normalized genre string.

        """
        for idx, provider_genre_list in self._provider_genre_map:
            for provider_genre in provider_genre_list:
                if genre.strip().upper() == provider_genre.upper():
                    idx, de, en = self._global_genre_map[int(idx)]
                    if output_lang == 'de':
                        return de.strip()
                    else:
                        return en.strip()

    def normalize_genre_list(self, genre_list, output_lang='de'):
        """ A list wrapper for :func:`normalize_genre`. """
        normalized = []
        for genre in genre_list:
            normalized_genre = (self.normalize_genre(genre, output_lang))
            if normalized_genre is not None:
                normalized.append(normalized_genre)
        return normalized
