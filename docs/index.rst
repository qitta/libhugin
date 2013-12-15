.. title is not shown in flask theme:

Libhugin documentation.
=======================

Libhugin Introduction
---------------------

.. warning::

    Libhugin is under heavy developement and may not be suitable for productive
    usage yet. The library currently supports Python 3.3+ only.

*Libhugin* is a modular movie metadata search and analysis library written in
python. The goal is to provide webservice independent unique API for different
kind of movie metadata. The library is divided into two parts, the :ref:`core`
part, which is responsible for fetching all the metadata and the :ref:`analyze`
part for analyzing a existing movie collection to improve its quality by
detecting missing metadata or extracting new information from the existing
collection.

In short - libhugin's goal is to be fast and flexible by providing a *simple and
extensible* library which is also suitable for scripting tasks.

For a short demo - let's search for the movie **Sin City**:

.. code-block:: python

   >>> from hugin.core import Session

   >>> session = Session() # Create a sesion.
   >>> query = session.create_query(title='Sin City') # Create a query.
   >>> results = session.submit(query) # Search it!

   >>> print(results)

   ... [<TMDBMovie <picture, movie> : Sin City (2005)>,
   ...  <OFDBMovie <movie> : Sin City (2005)>,
   ...  <OMDBMovie <movie> : Sin City (2005)>]


Easy as pie - isn't it?

The same way you can search for person metadata. It is also possible to search
by *imdb* movie id. For more information about library usage see:
:ref:`libraryusage`.

For simple scripting task or console usage there is also a minmalistic client
available, see: :ref:`clientusage`.

.. _core:

libhugin core
~~~~~~~~~~~~~

The libhugin core part is responsible for fetching metadata from different
webservices like

    * `TMDB <http://www.themoviedb.org/documentation/api>`_
    * `OFDB <http://www.ofdbgw.org>`_
    * `OMDB <http://www.omdbapi.com>`_

to search for movie and person metadata including pictures.

As libhugin is a modular library, you can write a content provider yourself and
extend libhugins search horizon. For provider plugin development see developer
section: :ref:`pluginapi`


.. _analyze:

libhugin analyze
~~~~~~~~~~~~~~~~

Currently, the analyze part's purpose is to identify missing or invalid metadata
to improve the quality of a existing movie collection.  For more information
about libhugins analyze part see: `libhugin analyze.`

The analyze part of the library might be extended to analyse and harvest new
information from your movie collection anytime soon. This could be done by using
different data mining algorithms and do stuff like:

    * extracting plot keywords
    * analyse similary of movies by genre, director, etc...


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
