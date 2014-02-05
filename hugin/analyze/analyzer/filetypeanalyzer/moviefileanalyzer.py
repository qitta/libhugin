#!/usr/bin/env python
# encoding: utf-8

import subprocess
from functools import reduce
import os

# 3rd party
import yaml

# hugin
import hugin.analyze as plugin


MOVIE_FILESIZE = (1 * 1024 ** 2)


class MovieFileAnalyzer(plugin.IAnalyzer):

    def process(self, movie):
        movie_metadata = []
        for moviefile in self._get_movie_files(movie.key):
            output = subprocess.check_output(
                ['hachoir-metadata', '--raw', moviefile]
            )
            metadata_clean = self._concat_yaml_dict(yaml.load(output))
            file_metadata = (moviefile, metadata_clean)
            movie_metadata.append(file_metadata)
        movie.analyzer_data[self.name] = movie_metadata

    def _get_movie_files(self, path, threshold=MOVIE_FILESIZE):
        movie_files = []
        files = [os.path.join(path, item) for item in os.listdir(path)]
        for moviefile in files:
            if os.path.getsize(moviefile) > threshold:
                movie_files.append(moviefile)
        return movie_files

    def _concat_yaml_dict(self, yamldict):
        for key, attr in yamldict.items():
            yamldict[key] = self._concat_dicts(attr)
        return yamldict

    def _concat_dicts(self, attr):
        return reduce(lambda x, y: dict(x, **y), attr)
