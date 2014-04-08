.. currentmodule:: hugin.harvest.provider

.. _pluginapi:

############
Introduction
############


.. note::

   This section is for developers who wants to write plugins for libhugin. If
   you just want to use the library as it is, see :ref:`libraryusage`.


To write plugins for libhugin you need to get to know the project structure
first. Here is a overview of the structure where provider, prostprocessing and
converter plugins are located. The overview is shortened.

.. _libhugin_project_structure:

libhuin project structure
=========================

.. code-block:: sh

    hugin
    ├── analyze
    ├── harvest
    │   ├── cache.py
  * │   ├── converter    <-- converter plugin folder
    │   │   ├── html
    │   │   │   ├── html.py
    │   │   │   └── [...]
    │   │   └── json
    │   │       ├── __init__.py
    │   │       ├── json.py
    │   │       └── json.yapsy-plugin
    │   ├── downloadqueue.py
    │   ├── __init__.py
    │   ├── pluginhandler.py
  * │   ├── postprocessor   <-- postprocessor plugin folder
    │   │   ├── compose
    │   │   │   ├── compose.py
    │   │   │   ├── compose.yapsy-plugin
    │   │   │   └── __init__.py
    │   │   └── trim
    │   │       └── [...]
  * │   ├── provider    <-- provider plugin folder
  * │   │   ├── genrefiles <-- provider subfolder with genre norm data
    │   │   │   ├── normalized_genre.dat
    │   │   │   ├── tmdb.genre
    │   │   │   └── [...]
    │   │   ├── __init__.py
    │   │   ├── genrenorm.py
    │   │   ├── result.py
    │   │   ├── omdb
    │   │   │   ├── __init__.py
    │   │   │   ├── omdbmovie.py
    │   │   │   └── omdbmovie.yapsy-plugin
    │   │   ├── ofdb
    │   │   │   └── [...]
    │   │   └── tmdb
    │   │       └── [...]
    │   ├── query.py
    │   └── session.py
    ├── __init__.py
    ├── __main__.py
    └── utils
        ├── __init__.py
        ├── logutil.py
        └── stringcompare.py

.. _pluginsys:

Libhugin plugin system
======================

Currently the plugin system is based on yapsy, so you will need to define a
*.yapsy-plugin*-file according to the yapsy plugin convention.

In the following snippet, you see examplar the converter dictionary. No matter
if a content provider, output converter or postprocessor plugin the structure
is analogue to the following converter example:

.. code-block:: sh

    hugin
    ├── harvest
    │   ├── cache.py
    │   ├── converter           <-- converter plugin folder.
    │   │   └── json            <-- json plugin, a module containing the
    │   │       ├── __init__.py     implementation and a yapsy plugin description file.
    │   │       ├── json.py
    │   │       └── json.yapsy-plugin


The plugin itself is located in a folder with a __init__.py to make it act as a
module. The plugin itself in this case is the json.py file, in this case this is
a class inheriting from the postprocessor interface implementing the needed
methods. The *.yapsy-plugin* file is a description file that should name and
describe the plugin precisely.

Json yapsy description examlple:

::

    [Core]
    Name = JSON    # plugin name used by libhugin.
    Module = json  # name of the plugin implementation without py ending.

    [Documentation]
    Description = Converts result object to json format.  # description used by libhugin.
    Author = Christoph Piechula
    Version = 1.0
    Website = n/a


The name attrubute inside the yapsy plugin file is the name the plugin will be
available at libhugin. The description is the description of the plugin that
will be used als description inside libhugin too.

For more information about yapsy plugin shema, see `Yapsy plugin manager doc <https://yapsy.readthedocs.org/en/latest/PluginManager.html>`_
for general information and `Yapsy plugin info file convention <https://yapsy.readthedocs.org/en/latest/PluginManager.html#plugin-info-file-format>`_
for plugin description file.



.. _providerapi:

####################################
Developing a content provider plugin
####################################

Developing a content provider you will have to write a module according to the
yapsy specification, see :ref:`pluginsys`

Currently there are two types of metadata supported by libhugin. Movie- and
person metadata. All movie content provider have to inherit from
:class:`IMovieProvider` and all person provider from :class:`IPersonProvider`.


IMovieProvider
==============

.. autoclass:: hugin.harvest.provider.IMovieProvider

.. _genrenorm:

Genre *'normalization'*
-----------------------

By using different webservices, you probably will also get different tagged
data. As movie genre attributes are not standardized a webservice A may retrun
for the movie like Star Trek the genre *Science Fiction*, another webservice
will return for the same movie the genre *SciFi*, or *Sci-Fi* oder even
*Science-Fiction*.

This should't be a problem at first, but if you want to compare movies or
grouping them by genre to select a Science Fiction movie for your movie night,
this might get a problem if movies are tagged with different provider metadata.

As genre is a importent criteria for movie grouping and comparsion, libhugin
offers a simple genre normalization possibilty.

Inside the provider folder there is a genrefiles folder, see: :ref:`libhugin_project_structure`.
This folder contains a normalized_genre.dat file, which contains a global genre
using the following structure:

::

    0, Abenteuer, Adventure
    [...]
    20, Katastrophenfilm, Disaster
    [...]
    25, Lovestory, Romance
    [...]
    32, Science Fiction, Science Fiction
    [...]
    40, Western, Western

The first value is a index representing the global genre, the second and third
value is the genre name, in currently in german and english language.

If you want to have a unique genre accros all content provider, your provider
will have to implement the genre normalization. A complete genre normalization
implementation for a provider is only possible if you know all the genre names a
webservice will deliver.

Let's assume your provider all genre names your provider is able to deliver are:

.. _genreexample:

.. code-block:: sh

    Sci-Fi
    Liebesfilm
    Katastropen-Film

An you want this provider specific genres to be normalized, so you will have to
write a providername.genre file and place it inside the genrefiles folder. In
this case the provider specific genre mapping file would look like this:

.. _genregenre:

.. code-block:: sh

    # global index, provider specific genre

    32, Sci-Fi
    25, Liebesfilm
    20, Katastropen-Film


Now using this mapping the genre using the genre nomalization would be mapped
like this:


.. code-block:: sh

   # mapping when using language de
   Sci-Fi -> Science Fiction
   Liebesfilm -> Lovestory
   Katestrophen-Film -> Katastrophenfilm

   # mapping when using language de
   Sci-Fi -> Science Fiction
   Liebesfilm -> Romance
   Katestrophen-Film -> Disaster

A complete more complete example using genre nomalization: :ref:`exemplar_movieplugin`.

.. _exemplar_movieplugin:

Exemplar Movie Provider Implementation
======================================

.. note::

   The following webservice **does not** exist, it's only a fictional webservice
   to create a examplar movie provider plugin.

Our webservice will return a json file on a http response. Let's assume it's
name is TSMB (The Static Movie Database). The webservice is available at
http://tsmd-webservice.org/api and is able to take the movie title or a imdb id
as parameter.

Querying the webservice with curl and searching for *Watchmen*:

.. code-block:: sh

    $curl http://tsmd-webservice.org/api/movie/Watchmen
    {"Title":"Watchmen","Year":"2009","Genre":"Action, Drama, Mystery",
    "Plot":"In October 1985, New York City police are investigating the
    murder...", "ImdbID":"tt0409459"}


Querying the webservice with curl and searching for the imdbid *tt0409459*:

.. code-block:: sh

    $curl http://tsmd-webservice.org/api/imdbid/tt0409459
    {"Title":"Watchmen","Year":"2009","Genre":"Action, Drama, Mystery",
    "Plot":"In October 1985, New York City police are investigating the
    murder...", "ImdbID":"tt0409459"}

First we will have to create a subfolder inside the hugin/provider folder named
tsmd and creating a __init__.py file inside of it. After doing this we create a
tsmdmovie.py (the provider implementation) and a tsmdmovie.py (the plugin
description) file, which is needed by yapsy, see :ref:`pluginsys`.

As we want to use genre normalization (:ref:`genrenorm`), we will also create a
tsmd.genre file.

Creating our provider skeleton files:

.. code-block:: sh

    $touch hugin/provider/__init__.py
    $touch hugin/provider/tsmdmovie.py
    $touch hugin/provider/tsmdmovie.yapsy-plugin
    $touch hugin/provider/genrefiles/tsmd.genre


Lets check our structure:

.. code-block:: sh

   $ls -l hugin/provider
   total 0
   -rw-r--r-- 1 christoph users 0 Jan  5 15:53 __init__.py
   -rw-r--r-- 1 christoph users 0 Jan  5 15:53 tsmdmovie.py
   -rw-r--r-- 1 christoph users 0 Jan  5 15:53 tsmdmovie.yapsy-plugin

   $ls -l hugin/provider/genrefiles
   total 0
   -rw-r--r-- 1 christoph users 0 Jan  5 15:53 normalized_genre.dat
   -rw-r--r-- 1 christoph users 0 Jan  5 15:53 tsmd.genre


Filling in the *'.yapsy-plugin'* file with content:

::

    [Core]
    Name = TSMDMovie    # name our plugin will be known by libhugin
    Module = tmsdmovie  # this is the implementation filename without py ending

    [Documentation]
    Description = Default Movie meta data provider for TSMD Webservice.
    Author = W.W.
    Version = 1.0
    Website = www.tsmd-webservice.org/api/  # webservice api documentation


We assume that our provider is able to deliver the same genre attributes as seen
in the genre normalization example: :ref:`genreexample`, so the content of our
tsmd.genre file looks like this example: :ref:`genregenre`.

Filling in the *tsmdmovie.py* file with content:

.. code-block:: python

    #!/usr/bin/env python
    # encoding: utf-8

    #stdlib
    import json

    #hugin
    import hugin.harvest.provider as provider
    from hugin.harvest.provider.genrenorm import GenreNormalize

    # if our provider would also/only deliver picture content we would have to
    # inherit from *provider.IMoviePictureProvider* too.
    class TSMDMovie(provider.IMovieProvider):

        def __init__(self):
            # our api url
            self._base_url = 'http://www.tsmd-webservice.org/api/{stype}/{query}'

            # enabling genre normalization telling the normalizer which file to
            # be used
            self._genrenorm = GenreNormalize('tmsd.genre')

            # setting provider priority to 50, there is currently no rule for
            # this, higher priority provider will be definitly prefered when
            # picking results
            self._priority = 50

            # lets define all attributes our webservice will deliver
            self._attrs = {
                'title', 'year', 'plot', 'imdbid', 'genre', 'genre_norm'
            }

        def build_url(self, search_params):

            # if there is a imdbid we first try to build url out of it
            if search_params.imdbid:
                return [self._base_url.format(
                    stype='imdbid', query=search_params.imdbid
                )]

            # no imdbid, so let's look for title, else None will be returned
            if search_params.title:
                return [self._base_url.format(
                    stype='movie', query=search_params.title
                )]

        def parse_response(self, url_response, search_params):

            # getting the raw data and converting json to a python dict
            url, response = url_response.pop()

            # minimalistic check, if response seems to be valid and non empty
            # you will have to do real error handling here!
            if response:
                response = json.loads(response)

                # now we assume that our provider has delivered a json with a
                # single result, so we can start filling in the result dict

                # in real world we might have to pick out the result we want
                # from a list of possible movie titles, parse it and create a
                # list with urls to fetch next returning a tuple like
                # ([[url_movie_1], [url_movie_2]..], False)

                # lets build a clean result dict according to  the parameters
                # the webservice might deliver :)
                result_dict = {key: None for key in self._attrs}

                # filling in and returning our result dict
                # in real world you might have to format or convert the raw data
                # according to the IMovieProvider specs.
                result_dict['title'] = response['Title']
                result_dict['year'] = response['Year']
                result_dict['plot'] = response['Plot']
                result_dict['imdbid'] = response['ImdbID']
                result_dict['genre'] = response['Genre']

                # telling the genre normalizer to give us a normalized genre
                result_dict['genre_norm'] = self._genrenorm.normalize_genre_list(
                    result_dict['genre']
                )
                return result_dict, True

            # if all positive cases fail, we are finished without result
            return None, True


IPersonProvider
===============

.. autoclass:: hugin.harvest.provider.IPersonProvider

Whether a content provider supports only textual metadata or is also able to
fetch provider picture metadata, you may need to inherit from the
*PictureProvider* class too. If your provider will be able to search for art
metadata or even  art metadata only. To achieve this movie content provider have
to additionally inherit from :class:`IMoviePictureProvider` and person content
provider from :class:`IPersonPictureProvider`.


Content provider methods
========================

All content provider plugins have to implement at least the two methods
:meth:`IProvider.build_url` and :meth:`IProvider.parse_response`.

The build url method
====================

.. automethod:: hugin.harvest.provider.IProvider.build_url

The parse reponse method
========================

.. automethod:: hugin.harvest.provider.IProvider.parse_response


.. _postprocessorapi:

##################################
Developing a postprocessor plugin
##################################

All postprocessor plugins have to inherit from :class:`IPostprocessor` and
implement the following method:

.. automethod:: hugin.harvest.provider.IPostprocessor.process


.. _outputconverterapi:

####################################
Developing a output converter plugin
####################################

All output converter plugins have to inherit from :class:`IConverter` and
im implement the following method:

.. automethod:: hugin.harvest.provider.IConverter.convert
