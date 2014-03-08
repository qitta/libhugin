#!/usr/bin/env python
# encoding: utf-8

import re

from flask import Flask
from flask import Response

import hugin.harvest.session as HarvestSession
import hugin.analyze.session as AnalyzerSession


app = Flask(__name__)

SESSION = HarvestSession.Session()
ANALYZER = AnalyzerSession.Session('/tmp/dummydb')
CACHE = {}


def _build_search_results(results):
    enities = []
    CACHE.clear()
    for num, result in enumerate(results):
        template = _read_template('tools/huginproxy/result_enity.xml')
        enities.append(
            template.format(
                title=result._result_dict['title'],
                year=result._result_dict['year'],
                imdbid=result._result_dict['imdbid'],
                nr=num
            )
        )
        postprocess(result)
        CACHE[num] = result
    return ''.join(enities)


@app.route('/search/<title>')
def search(title):
    imdbid = re.findall('tt\d+', title)
    # search by imdbid
    if imdbid:
        query = SESSION.create_query(
            imdbid=imdbid.pop(), providers=['tmdbmovie'], language='de'
        )
    else:
    # search by title
        query = SESSION.create_query(
            title=str(title), fuzzysearch=True,
            providers=['tmdbmovie'], language='de'
        )
    results = SESSION.submit(query)
    template = _read_template('tools/huginproxy/results.xml')
    return Response(
        template.format(results=_build_search_results(results)),
        mimetype='text/xml')


@app.route('/movie/<num>')
def get_movie(num):
    result = CACHE[int(num)]
    nfo_converter = SESSION.converter_plugins('nfo')
    nfo_file = nfo_converter.convert(result)
    return Response(nfo_file, mimetype='text/xml')


def postprocess(result):
    plotcleaner = ANALYZER.modifier_plugins('plot')
    result._result_dict['plot'] = ANALYZER.process_raw(
        plotcleaner, 'plot', result._result_dict['plot']
    )


def _read_template(template):
    with open(template, 'r') as f:
        return f.read()

if __name__ == "__main__":
    app.run()
