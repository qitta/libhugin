.. _usermanual:

Libhugin usage
==============

.. _cmdtool:

Using libhugin commandline tool
--------------------------------

Libhugin has the small commandline tool called `gylfie <http://guardiansofgahoole.wikia.com/wiki/Gylfie>`_. It's suitable for console
junkies and simple scripting tasks.

::

    $ gylfie -h

    Libhugin commandline tool.

    Usage:
      gylfie.py (-t <title>) [-y <year>] [-a <amount>] [-p <providers>...] [-c <converter>] [-o <path>]
      gylfie.py (-n <name>) [--items <num>] [-p <providers>...] [-c <converter>] [-o <path>]
      gylfie.py (-i <imdbid>) [-p <providers>...] [-c <converter>] [-o <path>]
      gylfie.py list-provider
      gylfie.py list-converter
      gylfie.py -h | --help
      gylfie.py --version

    Options:
      -t, --title=<title>               Movie title.
      -y, --year=<year>                 Year of movie release date.
      -n, --name=<name>                 Person name.
      -i, --imdbid=<imdbid>             A imdbid prefixed with tt.
      -p, --providers=<providers>       Providers to be useed.
      -c, --convert=<converter>         Converter to be useed.
      -o, --output=<path>               Output folder for converter result.
      -a, --amount=<amount>             Amount of items you want to get.
      -v, --version                     Show version.
      -h, --help                        Show this screen.



Searching for the movie *Oldboy* released in 2003:

::

    $ hugin --title Oldboy --year 2003

    # Provider: TMDBMovie <picture, movie>

    Title: Oldboy (2003), imdbid: tt0364569, raiting: 7.5
    Cover Url: [('w92', 'http://image.tmdb.org/t/p/w92/fct7n9V10E8t8a7wOR90Ccw0i48.jpg')]
    Director: ['Chan-wook Park']
    Plot: Oldboy is the revenge drama from Director Park Chan-wook. Based on a
    Manga comic [...]

    # Provider: OFDBMovie <movie>

    Title: Oldboy (2003), imdbid: tt0364569, raiting: 8.31
    Cover Url: [(None, 'http://img.ofdb.de/film/43/43066.jpg')]
    Director: ['Park Chan-wook']
    Plot: Besonders familiär ist das Leben von Oh Dae-Su (Min-Sik Choi) nicht
    [...]

    # Provider: OMDBMovie <movie>

    Title: Oldboy (2003), imdbid: tt0364569, raiting: 8.4
    Cover Url: [(None, 'http://ia.media-imdb.com/images/M/MV5BMTI3NTQyMzU5M15BMl5BanBnXkFtZTcwMTM2MjgyMQ@@._V1_SX300.jpg')]
    Director: ['Chan-wook Park']
    Plot: An average man is kidnapped and imprisoned in a shabby cell for 15
    [...]


Searching for the person *Emma Stone*:

::

    $ hugin --name 'Emma Stone'

    # Provider: TMDBPerson <person, picture>

    Name: Emma Stone
    Photo: None found
    Biography: Emily Jean "Emma" Stone is an American actress best known for
    her deadpan acting style, husky voice, and red hair.
    [...]

    # Provider: OFDBPerson <person>

    Name: Emma Stone
    Photo: [(None, 'http://www.ofdb.de/images/person/3/3415.jpg')]
    Biography: None found.
    Known for: None found.

    # Provider: OFDBPerson <person>

    Name: Emma Stone
    Photo: [(None, 'http://www.ofdb.de/images/person/na-w.gif')]
    Biography: None found.
    Known for: None found.


The commandline tool makes only use of basic libhugin features. If you need
more power and control of what is going on look at the library itself.

.. _libraryusage:

Library usage tutorial
----------------------

.. autoclass:: hugin.core.session.Session
   :members: __init__, create_query,  submit, submit_async, cancel, clean_up, provider_plugins, postprocessing_plugins, converter_plugins,
