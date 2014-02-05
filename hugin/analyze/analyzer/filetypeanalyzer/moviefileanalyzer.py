#!/usr/bin/env python
# encoding: utf-8

# hugin
import hugin.analyze as plugin
import subprocess
import os
import yaml


MOVIE_FILESIZE = (1*1024**2)


class MovieFileAnalyzer(plugin.IAnalyzer):

    def process(self, movie):
        movie_metadata = []
        for moviefile in self._get_movie_files(movie.key):
            output = subprocess.check_output(
                ['hachoir-metadata', '--raw', moviefile]
            )
            file_metadata = (moviefile, yaml.load(output))
            movie_metadata.append(file_metadata)
        movie.analyzer_data[self.name] = movie_metadata

    def _get_movie_files(self, path, threshold=MOVIE_FILESIZE):
        movie_files = []
        files = [os.path.join(path, item) for item in os.listdir(path)]
        for moviefile in files:
            if os.path.getsize(moviefile) > threshold:
                movie_files.append(moviefile)
        return movie_files
