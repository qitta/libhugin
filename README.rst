###################################
libhugin - A movie metadata library
###################################

**Note:** Library is currently under developement.

Libhugin is a modular movie metadata retrieval and analysis library. It is
divided in two main parts:

**libhugin core**, the metadata retrieval part.

    + Responsible for getting the metadata from e.g. tmdb.org, ofdb.de, ...
    + A simple unique interface for all metadata providers
    + Metadata provider can get different types of metadata like

      - movie title, plot, etc
      - movie posters, backdrops
      - person details
      - person photos
      - etc

Besides the python api, the core library has a standalone ``libhugin client``
which makes it possible to use the library for automated scripting tasks.


**libhugin analyze**, the metadata analysis part.

The analysis part of the library is designed for ``experimental purposes`` at
first. It makes use of different data mining algorithms to e.g.:

    + extract plot keywords
    + analyse similary of movies by plot, genre, director, etc, ...
    + etc

Its purpose is to analyze and improve an existing movie database by harvesting
new information.


Installation
============

.. image:: https://travis-ci.org/qitta/libhugin.png?branch=master
    :target: https://travis-ci.org/qitta/libhugin



Required Python Modules
-----------------------

All modules are Python3 compatible:

.. code-block:: bash

    $ sudo pip install charade   # A Universal character encoding detector.
    $ sudo pip install yapsy     # A library for implementing a plugin system.

Optional dependencies:

.. code-block:: bash

    $ sudo pip install colorlog  # Colorful messages for the commandline.
