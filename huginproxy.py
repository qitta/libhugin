#!/usr/bin/env python
# encoding: utf-8

import re

from flask import Flask
from flask import Response

from hugin.harvest.session import Session


app = Flask(__name__)
SESSION = Session()
CACHE = {}


def _build_search_results(results):
    enities = []
    CACHE.clear()
    for num, result in enumerate(results):
        title = result._result_dict['title']
        imdbid = result._result_dict['imdbid']
        year = result._result_dict['year']
        tmp = """<entity>
            <title>{title} ({year}), [{imdbid}]</title>
            <url>http://localhost:5000/movie/{nr}</url>
        </entity>
        """.format(title=title, year=year, imdbid=imdbid, nr=num)
        print(tmp)
        enities.append(tmp)
        CACHE[num] = result._result_dict
    return ''.join(enities)


@app.route('/search/<title>')
def search(title):
    imdbid = re.findall('tt\d+', title)
    if imdbid:
        query = SESSION.create_query(
            imdbid=imdbid.pop(), providers=['tmdbmovie'], language='de'
        )
    else:
        query = SESSION.create_query(
            title=str(title), fuzzysearch=True,
            providers=['tmdbmovie'], language='de'
        )
    result = SESSION.submit(query)
    string = """<?xml version="1.0" encoding="iso-8859-1" standalone="yes"?>
    <results>
        {results}
    </results>
    """.format(results=_build_search_results(result))
    return Response(string, mimetype='text/xml')


@app.route('/movie/<num>')
def get_movie(num):
    result = CACHE[int(num)]
    poster = result.get('poster')
    if poster:
        _, result['poster'] = poster.pop()
    else:
        result['poster'] = ''
    string = """<?xml version="1.0" encoding="iso-8859-1" standalone="yes"?>
     <details>
        <title>{title}</title>
        <year>{year}</year>
        <director></director>
        <top250></top250>
        <mpaa></mpaa>
        <tagline></tagline>
        <runtime></runtime>
        <thumb>{poster}</thumb>
        <credits></credits>
        <rating></rating>
        <votes></votes>
        <genre></genre>
        <actor>
            <name></name>
            <role></role>
        </actor>
        <outline></outline>
        <plot>{plot}</plot>
 </details>
    """.format(**result)
    return Response(string, mimetype='text/xml')


if __name__ == "__main__":
    app.run()
