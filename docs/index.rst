.. title is not shown in flask theme:

Libhugin documentation.
=======================

Introduction
------------

**libhugin** is a modular movie metadata search and analysis library written in
python. The goal is to provide a unique API for different kind of metadata and
provider. The library is devided into two parts, the ``core`` part, which is
responsible for fetching all the metadata and the ``analyze`` part for analyzing
a existing movie collection with the goal to improve the quality of the
metadata. The goal is to provider a extensible library which is also suitable
for scripting tasks.

.. warning::

    Libhugin is under heavy developement and may not be suitable for productive
    usage yet.


**Simple pythonic usage:**

If you want to search for a movie, e.g. ``Only God Forgives``:

.. code-block:: python

   from hugin.core import Session

   session = Session()  # Create a sesion.
   query = session.create_query(title='Only God Forgives')  # Create a query.
   results = session.submit(query)  # Search it!

   print(results)

    [<TMDBMovie <picture, movie> : Only God Forgives (2013)>,
     <OFDBMovie <movie> : Only God Forgives (2013)>,
     <OMDBMovie <movie> : Only God Forgives (2013)>]


Easy as pie - isn't it?

The libhugin core part is responsible for fetching metadata from different
content providers like:

    * TMDB (movie, person, backdrops, photos, ...)
    * OFDB (movie, person metadata, ...)
    * OMDB (movie metadata, ...)


As libhugin is a modular library, you can write your provider yourself and
extend libhugins horizon. For provider plugin development see: developer section.

The analysis part of the library is designed to analyse a existing database at
first. It might be extended to analyse and harvest new information from your
movie collection anytime soon. This could be done by using different data mining
algorithms and do stuff like:

    * extracting plot keywords
    * analyse similary of movies by:

      + genre
      + director
      + etc

Lihugin's analyze purpose is to analyze and improve the quality of an existing
movie database by harvesting new information. For more information about
libhugins analyze part see "dokumentation analyze1"

Table of Contents
-----------------

**Architecture**

.. toctree::
    :glob:
    :maxdepth: 2

    architecture/*

**User Manual**

.. toctree::
    :glob:
    :maxdepth: 2

    user_manual/*

**Developer Section**

.. toctree::
    :glob:
    :maxdepth: 3

    developer_api/*




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
