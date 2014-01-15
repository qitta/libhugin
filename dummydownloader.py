#!/usr/bin/env python
# encoding: utf-8

import json
import os
import sys
import time

from hugin.core.session import Session

if __name__ == '__main__':
    s = Session()

    with open('imdbid_huge.txt', 'r') as f:
        movieids = f.read().splitlines()

    length = len(movieids)
    cnt = 0

    for movieid in movieids:
        movie = s.submit(s.create_query(
            imdbid=movieid, lang='de', providers=['tmdbmovie'])
        )
        if movie == []:
            print(movieid, ' not found.')
            continue
        movie = movie.pop()
        title = movie.result_dict['title']
        if '/' in title:
            title = title.replace('/', '|')
        moviefolder = '{0} ({1})'.format(title, movie.result_dict['year'])
        moviepath = 'movies/{}'.format(moviefolder)
        if not os.path.exists(moviepath):
            os.mkdir(moviepath)
        else:
            print(moviepath, movieid, ' exists.')

        with open('{0}/{1}.nfo'.format(moviepath, moviefolder), 'w') as f:
            f.write(json.dumps(movie.result_dict))
        print('Downloading: {} [{}/{}]'.format(movieid, cnt, length), end='\r')
        cnt += 1

