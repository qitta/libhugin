#!/usr/bin/env python
# encoding: utf-8

# stdlib
import re

# 3rd party libs
from flask import Flask
from flask import Response
from flask import request

# hugin
import hugin.harvest.session as HarvestSession
import hugin.analyze.session as AnalyzerSession


SESSION = HarvestSession.Session()
ANALYZER = AnalyzerSession.Session('/tmp/dummydbforanalyzer')

POSTPROCESSING = False
CACHE = {}

app = Flask(__name__)


##############################################################################
# -------------------------- flask functions ---------------------------------
##############################################################################

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
    """ Get movie with a specific number. """
    if CACHE:
        result = CACHE[int(num)]
        if POSTPROCESSING:
            postprocess(result)
        nfo_converter = SESSION.converter_plugins('nfo')
        nfo_file = nfo_converter.convert(result)
        return Response(nfo_file, mimetype='text/xml')
    return Response('Cache is empty.', mimetype='text')


@app.route('/stats')
def stats():
    response = 'Postprocessor enabled: {}\nResults in queue: {}'.format(
        POSTPROCESSING,
        len(CACHE)
    )
    return Response(response, mimetype='text')


@app.route('/toggle_pp')
def toggle_pp():
    try:
        global POSTPROCESSING
        POSTPROCESSING = not POSTPROCESSING
    except Exception as e:
        print(e)
    return 'Postprocessor enabled: {}'.format(POSTPROCESSING)


@app.route('/shutdown')
def shutdown():
    print('Shutting down hugin...')
    SESSION.cancel()
    SESSION.clean_up()
    ANALYZER.database_shutdown()
    print('Shutting down server...')
    shutdown_server()


##############################################################################
# -------------------------- helper functions --------------------------------
##############################################################################

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
                provider=result._provider.name,
                nr=num
            )
        )
        CACHE[num] = result
    return ''.join(enities)


def postprocess(result):
    """ Postprocess example. """
    bracketclean = ANALYZER.modifier_plugins('bracketclean')
    result._result_dict['plot'] = ANALYZER.modify_raw(
        bracketclean, 'plot', result._result_dict['plot']
    )


def _read_template(template):
    """ Helper for reading templates. """
    with open(template, 'r') as file:
        return file.read()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('No werkzeug server running.')
    func()

if __name__ == "__main__":
    app.run()
