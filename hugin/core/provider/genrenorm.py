#!/usr/bin/env python
# encoding: utf-8

""" Genre normalization module. """

import pkgutil


class GenreNormalize:
    """
    Normalize genre according to given provider genre mapping files.

    public methods:

        normalize_genre(genre)
        normalize_genre_list(genre_list)

    """
    def __init__(self, provider_genre_file):
        """
        Create a genrenormalize object for a specific provider.

        The provider genre file naming should be 'providername.genre'. The
        mapping is done according to the genres indexes in the
        normalize_genre.dat file.

        Global genre mapping file content snippet :

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
            12, Fan Film, Fan Film
            13, Fantasy, Fantasy

        Provider genre mapping file example ::

            0, Abenteuer
            1, Action
            10, Experimentalfilm
            11, Kinder-/Familienfilm
            13, Fantasy


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
                __package__, 'normalized_genre.dat'
            )
            provider_genre_bytes = pkgutil.get_data(
                __package__, provider_genre_file
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

    def print_mapping(self):
        """ Print current mapping - for test purposes only. """
        for idx_genre in self._provider_genre_map:
            idx, genres = idx_genre
            for genre in genres:
                genre = genre.strip()
                print(genre, '-->', self.normalize_genre(genre, 'de'))

    def _strip_genre_string(self, genre_list):
        """ Strip genre string. """
        cleaned = []
        for genre in genre_list:
            cleaned.append(genre.strip())
        return cleaned

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
        for genre in genre_filerepr.splitlines():
            num, de, en = self._strip_genre_string(genre.split(','))
            genre_map.append((num, de, en))
        return genre_map

    def _create_provider_genre_map(self, genre_filerepr):
        """
        Create a provider specific genre mapping.

        This function is the counterpart to :func:`_create_global_genre_map`.

        """
        genre_map = []
        for genre in genre_filerepr.splitlines():
            idx, *genre_filerepr = genre.split(',')
            clean_genre_list = []
            for genre in genre_filerepr:
                clean_genre_list += self._strip_genre_string(genre.split(','))
                clean_genre_list = list(set(clean_genre_list))
                item = (idx, (clean_genre_list))
            genre_map.append(item)
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
