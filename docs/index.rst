.. Libhugin documentation master file, created by
   sphinx-quickstart on Wed Oct 30 15:21:12 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Libhugin documentation.
=======================

**Introduction**

**libhugin** is a modular movie metadata search and analysis library written in
python. The goal is to provide a unique API for different kind of metadata and
provider. The library is devided into two parts, the ``core`` part, which is
responsible for fetching all the metadata and the ``analyze`` part for analyzing
a existing movie collection with the goal to improve the quality of the
metadata.

The core part is responsible for fetching metadata from different content
providers like:

    * TMDB (movie, person, backdrops, photos, ...)
    * OFDB (movie, person metadata, ...)
    * OMDB (movie metadata, ...)
    * ...

The core library has a standalone libhugin client which makes it possible to use
the library for automated scripting tasks.

The analysis part of the library is designed for experimental purposes at
first. It makes use of different data mining algorithms to e.g.:

    * extract plot keywords
    * analyse similary of movies by plot,
    * genre, director, etc, ...
    * etc

Its purpose is to analyze and improve the quality of an existing movie database
by harvesting new information.


**Overview**

.. toctree::
    :glob:
    :maxdepth: 1

This is the overview.


**Architecture**

.. toctree::
    :glob:
    :maxdepth: 1

Here comes the architecture.

**API**

.. toctree::
    :glob:
    :maxdepth: 2

    api/*

Here comes theapi.

.. todo:: CONTENT!

.. todolist::


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
