.. currentmodule:: hugin.core.session

.. _cmdtool:

###############################
libhugin commandline tool usage
###############################



Libhugin has the small commandline tool that is meant to be used for *library
testing purposes* called `gylfie <http://guardiansofgahoole.wikia.com/wiki/Gylfie>`_.
It may also be suitable for console junkies and simple scripting tasks.

To get help, just use the *-h* parameter as usaual.

::

    $ gylfie -h

    Usage:
      gylfie (-t <title>) [-y <year>] [-a <amount>] [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>] [-P <pm>]  [-r <processor>] [-f <pfile>]
      gylfie (-i <imdbid>) [-p <providers>...] [-c <converter>] [-o <path>] [-l <lang>] [-r <processor>] [-f <pfile>]
      gylfie (-n <name>) [--items <num>] [-p <providers>...] [-c <converter>] [-o <path>]
      gylfie list-provider
      gylfie list-converter
      gylfie list-postprocessing
      gylfie -h | --help
      gylfie --version

    Options:
      -t, --title=<title>               Movie title.
      -y, --year=<year>                 Year of movie release date.
      -n, --name=<name>                 Person name.
      -i, --imdbid=<imdbid>             A imdbid prefixed with tt.
      -p, --providers=<providers>       Providers to be used.
      -c, --convert=<converter>         Converter to be used.
      -r, --postprocess=<processor>     Postprocessor to be used.
      -o, --output=<path>               Output folder for converter result [default: /tmp].
      -a, --amount=<amount>             Amount of items to retrieve.
      -l, --language=<lang>             Language in ISO 639-1 [default: de]
      -P, --predator-mode               The magic 'fuzzy search' mode.
      -f, --profile-file=<pfile>        User specified profile.
      -v, --version                     Show version.
      -h, --help                        Show this screen.


Searching for metadata
======================

.. note::

    The output of the command line tool in the examples is stripped down to a
    minimum, so don't get confused if your output is much more verbose :).

This chapter demonstrates with some simple examples the usage and possibilities
of the libhugin command line tool.


Searching for movies
--------------------

Searching by title
~~~~~~~~~~~~~~~~~~

Searching for the movie *Oldboy*, limiting the amount of results to two:

::

    $ gylfie --title oldboy --amount 2

    Provider: OMDBMovie <movie>

    Title       : Oldboy (2003), imdbid: tt0364569, raiting: 8.4
    Plot        : An average man is kidnapped and imprisoned in a [...]
    Directors   : ['Chan-wook Park']
    Genre       : ['Drama', ' Mystery', ' Thriller']


    Provider: OFDBMovie <movie>

    Title       : Oldboy (2013), imdbid: tt1321511, raiting: 4.15
    Plot        : None
    Directors   : ['Spike Lee']
    Genre       : ['Action', 'Drama', 'Mystery', 'Thriller']

We get two results, each from a different provider. In this case we get the
original *Oldboy* movie released in 2003 and the remake released in 2013.


Searching by title and year
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Well, seeing the result from the output above, we probably want to search for
the original release from 2003, not the remake. This can easily be done by
adding the release date to the search query.

This time without amount limit, but we limit the results to be only from
tmdbmovie and ofdbmovie provider:

::

    $ gylfie --title oldboy --year 2003 --providers ofdbmovie,tmdbmovie

    Provider: TMDBMovie <picture, movie>

    Title       : Oldboy (2003), imdbid: tt0364569, raiting: 7.5
    Plot        : 15 Jahre.  So lange wird Dae-su OH, ein ganz [...]
    Directors   : ['Chan-wook Park']
    Genre       : ['Action', 'Drama', 'Mystery', 'Thriller']


    Provider: OFDBMovie <movie>

    Title       : Oldboy (2003), imdbid: tt0364569, raiting: 8.31
    Plot        : None
    Directors   : ['Park Chan-wook']
    Genre       : ['Drama', 'Thriller']


Searching by imdbid
~~~~~~~~~~~~~~~~~~~

Sometimes it is useful if there is the possibility to search by imdb id. This
might also be good for automated scripting tasks if you want just to update a
existing movie metadata database. In this case searching for the movie title and
year might also give you invalid results if there are two movies with equal
title and year.

Let's just search for the movie *Drive*, released in 2011:

::

    $ gylfie --title drive --year 2011

    Provider: OFDBMovie <movie>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 7.81
    Plot        : „Ich fahre.“ So beantwortet der „Driver“ (Ryan Gosling) die [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Action', 'Drama', 'Thriller']


    Provider: TMDBMovie <picture, movie>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 6.6
    Plot        : Tagsüber arbeitet Driver unauffällig als Stuntfahrer [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Action', 'Krimi', 'Drama', 'Thriller']


    Provider: OFDBMovie <movie>

    Title       : Drive [Kurzfilm] (2011), imdbid: tt2072950, raiting: 0.00
    Plot        : None
    Directors   : ['Jean-Luc Julien']
    Genre       : ['Drama', 'Kinder-/Familienfilm']


As you can see, there seems to be another movie, well a short movie with the same
title and release date which was delivered by the ofdbmovie provider. To
minimize this problem while updating a existing database with libhugin, you
may want to search by imdbid which should give you exact results.

Searching for movie *Drive (2011)* by imdbid *tt0780504*, taken from above
search output. This time we use the language flag set to Netherlands, to get
the metadata in this language. Currently only tmdbmovie provider is able to
deliver multilanguage results.


::

    $ gylfie -i tt0780504 --language nl

    Provider: OFDBMovie <movie>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 7.81
    Plot        : „Ich fahre.“ So beantwortet der „Driver“ (Ryan Gosling) [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Action', 'Drama', 'Thriller']


    Provider: TMDBMovie <movie, picture>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 6.6
    Plot        : In Drive staat een Hollywood-stuntrijder centraal, een eenzaat van [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Actie', 'Misdaad', 'Drama', 'Thriller']


    Provider: OMDBMovie <movie>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 7.9
    Plot        : A mysterious man who has multiple jobs as a garage [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Crime', ' Drama']


Searching for a person
----------------------

.. note::

    Currently the postprocessing composer plugin is limited to movies only.
    There is also no imdbid person search, as this is not supported by the used
    webservices.

Searching for a person can be done analogue to the movie search. You just have to
use the *-n, --name* parameter.

Searching for the person *Emma Stone*:

::

    $ gylfie --name 'Emma Stone'

    Provider: TMDBPerson <person, picture>

    Name: Emma Stone
    Photo: None found
    Biography: Emily Jean "Emma" Stone is an American actress best known for [...]

    Provider: OFDBPerson <person>

    Name: Emma Stone
    Photo: [(None, 'http://www.ofdb.de/images/person/3/3415.jpg')]
    Biography: None found.

    Provider: OFDBPerson <person>

    Name: Emma Stone
    Photo: [(None, 'http://www.ofdb.de/images/person/na-w.gif')]
    Biography: None found.


Using postprocessing plugins with the commandline tool
======================================================

Composing your own movie results
--------------------------------

A result delivered by a specific provider might not always be what you want.
There might be missing some attributes or maybe you just want to get your
default metadata from provider TMDBmovie, but your plot always from the
OFDBmovie provider. This is the point where the postprocessing plugins comes
into play.


Automatic result composing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently there is a Composer provider, which allows you to compose your result
by your own needs.

The auto fill mode of the composer plugin is triggered if there is no user
specified profile file given:

::

    $  gylfie -i tt1937390 -r composer

    Provider: OMDBMovie <movie>

    Title       : Nymphomaniac: Part 1 (2013), imdbid: tt1937390, raiting:
    Plot        : A self-diagnosed nymphomaniac recounts her erotic experiences [...]
    Directors   : ['Lars von Trier']
    Genre       : ['Drama']


    Provider: TMDBMovie <movie, picture>

    Title       : Nymphomaniac (2013), imdbid: tt1937390, raiting: None
    Plot        : None
    Directors   : ['Lars von Trier']
    Genre       : ['Drama']

    Provider: OFDBMovie <movie>

    Title       : Nymphomaniac (2013), imdbid: tt1937390, raiting: 0.00
    Plot        : None
    Directors   : ['Lars von Trier']
    Genre       : ['Drama', 'Erotik', 'Sex']


    Provider: Composer

    Title       : Nymphomaniac (2013), imdbid: tt1937390, raiting: None
    Plot        : A self-diagnosed nymphomaniac recounts her erotic experiences [...]
    Directors   : ['Lars von Trier']
    Genre       : ['Drama']


The automatic mode of the composer creates the composer result according  to the
provider priority. Currently the priority is a constant value.

    * TMDBmovie priority = 90
    * OMDBmovie priority = 80
    * OFDBmovie priority = 70

The provider with the highest priority fills in the composer result first. As
you see in this case, there is missing the plot metadata attribute of the
tmdbmovie provider. This gets automatically filled in by the next available plot
from a lower priority provider. To fill all metadata found in the current query,
the composer fills in the missing tmdbmovie gap with the plot of the omdbmovie
provider data.


User specified result composing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Another feature is to tell the composer how to fill in the composer result. This
can be achieved by using a userprofile file formatted according to a python
dictionary.


User profiles
~~~~~~~~~~~~~

A user profile is formatted like a python dictionary. It has a *default* key,
which specifies a list with movie providers. The first available provider result
according to that list will be copied to be the composer result base. Besides
the default key you can specify movie attribute keys with a list of providers as
value. Those attributes will be filled in according to the same schema.

Creating a simple user profile for the composer postprocessing plugin:

::

    # lets create a profile first. tmdb should be the main supplier and
    # the plot should always come from ofdbmovie

    echo "{'default':['tmdbmovie', 'ofdbmovie'], 'plot':['omdbmovie', 'ofdbmovie']}" > userprofile

This profile will copy the tmdbmovie result and fill in it's plot with the
omdbmovie provider result attribute. If there is no tmdbmovie provider result,
the ofdbmovie provider result is copied. If the ofdbmovie plot attribute is
empty, the omdbmovie attribute will be filled in.

If there is no default provider available, no composer result will be created.
If the plot of the ofdbmovie and omdbmovie provider is missing, the plot
attribute will remain unchanged.

Now let's run the query with our beautiful profile:

::

    $ gylfie -i tt0780504 -r composer -f userprofile

    Provider: TMDBMovie <picture, movie>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 6.6
    Plot        : Tagsüber arbeitet Driver unauffällig als Stuntfahrer in [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Action', 'Krimi', 'Drama', 'Thriller']


    Provider: OMDBMovie <movie>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 7.9
    Plot        : A mysterious man who has multiple jobs as a garage [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Crime', ' Drama']


    Provider: OFDBMovie <movie>

    Title       : Drive (2011), imdbid: tt0780504, raiting: 7.81
    Plot        : „Ich fahre.“ So beantwortet der „Driver“ (Ryan Gosling) die [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Action', 'Drama', 'Thriller']


    Provider: Composer

    Title       : Drive (2011), imdbid: tt0780504, raiting: 6.6
    Plot        : „Ich fahre.“ So beantwortet der „Driver“ (Ryan Gosling) die [...]
    Directors   : ['Nicolas Winding Refn']
    Genre       : ['Action', 'Krimi', 'Drama', 'Thriller']


Using output converter plugins
==============================

It is also possible to use output converter plugins. This plugins are
responsible for formatting your result according to a specific manner. Currently
there are two basic output converter for json and html avaliable to demonstrate
how things work. You can combine those converters with a output directory.

Lets do a more *'complete'* example. This query gets a single result from the
provider tmdbmovie, formatting the result to json and writing it to the current
path:

::

    $  gylfie -t oldboy -y 2003 -a 1 -p tmdbmovie -c json -o .

    ** writing result as .json to ./TMDBMovie <picture, movie>.json.**

    Provider: TMDBMovie <picture, movie>

    Title       : Oldboy (2003), imdbid: tt0364569, raiting: 7.5
    Plot        : 15 Jahre.  So lange wird Dae-su OH, ein ganz durchschnittlicher
    Directors   : ['Chan-wook Park']



.. _libraryusage:

######################
Library usage tutorial
######################


This tutorial describes how to use the library.


Session usage
=============

First of all, you have to create a Session. This is the way to *communicate*
with the hugin library.

Creating a Session:


.. code-block:: python

    >>> # getting and intializing the session
    >>> from hugin.core import Session
    >>> session = Session()

There are some Session parameters e.g. the 'user-agent' that may be changed by
the user.

The following Session will use the user agent *'ravenlib/1.0'*.

.. code-block:: python

    >>> session = Session(user_agent='ravenlib/1.0')


For more information about session configuration parameters see: :class:`Session`.


Creating a query
================

After creating a :class:`Session`, you will need a query. The query represents
your *search* for a specific movie or person and may also be parametrized
individually. The query may be build by hand, but it's recommended to use the
session :meth:`Session.create_query` method. This method returns a validated
query.

The following query will search for the movie *Sin City*, the result amount is
limited to a max number of five items. Download retries are set to two.

.. code-block:: python

    >>> query = session.create_query(title='Sin City', amount=5, retries=2)
    >>> # just to illustrate how a query looks like
    >>> print(query)
    {'year': None, 'type': 'movie', 'providers': None, 'remove_invalid': True,
    'fuzzysearch': False, 'amount': 5, 'language': '', 'imdbid': None, 'retries': 2,
    'cache': True, 'strategy': 'flat', 'search': 'both', 'title': 'Sin City'}


You will just receive a dictionary representing the search values.  Depending on
the metadata type there are different parameters to be used in a query. For all
possible parameters see: :meth:`Session.create_query`.

Submiting a query
=================

After creating a session and getting a query you have to submit it by using
:meth:`Session.submit`. This is the point where libhugin starts to querying the
content provider to retrieve the metadata you are searching for. The
submit method will return a list with results found.

The following code block illustrates the query usage:

.. code-block:: python

    >>> results = s.submit(query)
    >>> print(result)
    [<TMDBMovie <movie, picture> : Sin City (2005)>,
    <OFDBMovie <movie> : Sin City (2005)>,
    <OMDBMovie <movie> : Sin City (2005)>]

The :meth:`Session.submit` method blocks. You can also submit the query
asynchronously by using the :meth:`Session.submit_async` method.


.. autoclass:: hugin.core.session.Session
   :members: create_query,  submit, submit_async, cancel, clean_up, provider_plugins, postprocessing_plugins, converter_plugins
