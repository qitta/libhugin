#!/usr/bin/env python
# encoding: utf-8

from collections import defaultdict
from functools import reduce
import subprocess
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
            normalized_metadata = self._normalize(metadata_clean)
            file_metadata = (moviefile, normalized_metadata)
            movie_metadata.append(file_metadata)
        movie.analyzer_data[self.name] = movie_metadata

    def process_database(self, db):
        for movie in db.values():
            self.process(movie)

    def _get_movie_files(self, path, threshold=MOVIE_FILESIZE):
        movie_files = []
        files = [os.path.join(path, item) for item in os.listdir(path)]
        for moviefile in files:
            if os.path.getsize(moviefile) > threshold:
                movie_files.append(moviefile)
        return movie_files

    def _normalize(self, attrs):
        attr_map = {
            'audio': {
                'language': 'language',
                'channels': 'nb_channel',
                'codec': 'compression'
            },
            'video': {
                'language': 'language',
                'width': 'width',
                'height': 'height',
                'codec': 'compression'
            },
            'subtitle': {
                'language': 'language'
            }
        }

        meta_grouped = {'audio': [], 'video': [], 'subtitle': []}
        for key, valuedict in attrs.items():
            if 'audio' in key:
                meta_grouped['audio'].append(valuedict)
            if 'video' in key:
                meta_grouped['video'].append(valuedict)
            if 'subtitle' in key:
                meta_grouped['subtitle'].append(valuedict)

        metadata = []
        for key, item in meta_grouped.items():
            metadata.append(
                self._extract_attr(meta_grouped[key], key, attr_map[key])
            )

        return reduce(lambda x, y: dict(x, **y), metadata)

    def _extract_attr(self, data, s_type, attrs):
        a_streams = defaultdict(dict)
        for num, stream in enumerate(data):
            key = '{}_{}'.format(s_type, num)
            for attr, fileattr in attrs.items():
                a_streams[key][attr] = stream.get(fileattr) or ''

            # we need to calculate video aspect ratio separately
            if 'video' in s_type:
                h, w = a_streams[key]['height'], a_streams[key]['width']
                if h and w:
                    a_streams[key]['aspect'] = round(w / h, 2)
        return a_streams

    def _concat_yaml_dict(self, yamldict):
        for key, attr in yamldict.items():
            yamldict[key] = self._concat_dicts(attr)
        return yamldict

    def _concat_dicts(self, attr):
        return reduce(lambda x, y: dict(x, **y), attr)
