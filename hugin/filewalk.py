#!/usr/bin/env python
# encoding: utf-8

import os
import glob
import xmltodict


def attr_mapping():
    return {
        'title': 'title', 'originaltitle': 'originaltitle', 'year': 'year',
        'plot': 'plot', 'director': 'director', 'genre': 'genre'
    }


##############################################################################
# -------------------------- import functions --------------------------------
##############################################################################
def attr_import_func(nfo_file, mask):
    try:
        with open(nfo_file, 'r') as f:
            xml = xmltodict.parse(f.read())
            attributes = {key: None for key in mask.keys()}
            for key, filekey in mask.items():
                attributes[key] = xml['movie'][filekey]
            return attributes
    except Exception as e:
        print('Exception', e)


def data_import(path):
    metadata = []
    for moviefolder in os.listdir(path):
        full_movie_path = os.path.join(path, moviefolder)
        nfofile = glob.glob1(full_movie_path, '*.nfo')
        if nfofile == []:
            nfofile = full_movie_path
        else:
            nfofile = os.path.join(full_movie_path, nfofile.pop())
        metadata.append(nfofile)
    return metadata


##############################################################################
# -------------------------- export functions --------------------------------
##############################################################################
def attr_export_func(movie):
    mask = attr_mapping()
    print(movie.nfo)
    with open(movie.nfo, 'r') as f:
        xml = xmltodict.parse(f.read())
        for key, filekey in mask.items():
            xml['movie'][filekey] = movie.attributes[key]
        with open(movie.nfo, 'w') as f:
            f.write(xmltodict.unparse(xml, pretty=True))


def data_export(metadata_dict):
    for movie in metadata_dict:
        attr_export_func(movie)
