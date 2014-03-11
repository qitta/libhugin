#!/usr/bin/env python
# encoding: utf-8

import json
import os
import sys



from hugin.harvest.session import Session

USAGE = """Usage:
python dummydownloader <foldertosave> <filewithimdbids> <provider>
"""

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(USAGE)
        sys.exit(1)

    s = Session(parallel_jobs=4, parallel_downloads_per_job=2)

    if os.path.exists(sys.argv[1]):
        print('{}, already exists.'.format(sys.argv[1]))
    else:
        print('Creating {}.'.format(sys.argv[1]))
        os.mkdir(sys.argv[1])

    with open(sys.argv[2], 'r') as f:
        movieids = f.read().splitlines()

    length = len(movieids)
    cnt = 0

    for movieid in movieids:
        movie = s.submit(s.create_query(
            imdbid=movieid, lang='de', providers=[sys.argv[3]], cache=True)
        )
        if movie == []:
            print(movieid, ' not found.')
            continue
        movie = movie.pop()
        title = movie.result_dict['title']
        if '/' in title:
            title = title.replace('/', '|')
        moviefolder = '{0} ({1})'.format(title, movie.result_dict['year'])
        moviepath = '{}/{}'.format(sys.argv[1], moviefolder)
        if not os.path.exists(moviepath):
            os.mkdir(moviepath)
        else:
            print(moviepath, movieid, ' exists.')

        with open('{0}/{1}.nfo'.format(moviepath, moviefolder), 'w') as f:
            f.write(json.dumps(movie.result_dict))
        print('Downloading: {} [{}/{}]'.format(movieid, cnt, length), end='\r')
        cnt += 1

