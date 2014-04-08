Architecture overview
=====================

.. figure:: /_static/archoverview.png
    :width: 100%


Libhugin is divided into two parts. A :ref:`harvest` and a :ref:`analyze` part. Both
parts are modular and may be extended by plugins.

.. _harvest:

libhugin harvest
================


The libhugin harvest part is responsible for fetching movie and person metadata
from different webservices like

    * `The Movie Database <http://www.themoviedb.org/documentation/api>`_
    * `Online-Filmdatenbank <http://www.ofdbgw.org>`_
    * `Open Movie Database <http://www.omdbapi.com>`_

As libhugin is a modular library, you can write a content provider yourself and
extend libhugins search horizon. For provider plugin development see developer
section: :ref:`pluginapi`

libhugin harvest makes use of the following plugins types:

    * :ref:`provplugin`
    * :ref:`postplugin`
    * :ref:`convplugin`

The modularity makes it easy to adapt hugin to your specific needs.

Plugins
=======

Libhugin is all about plugins. There are three different kinds of plugins that
libhugin harvest makes use of.

.. _provplugin:

Provider plugins
----------------

Provider Plugins are content provider that are responsible for fetching the
metadata from the web. This plugins act as ``proxy`` between a webservice  and
libhugin harvest. A webservice might be e.g. the TMDB API:

    * http://docs.themoviedb.apiary.io/

A provider plugin might also parse a html page if there is no api available.
It's up to the provider plugin. A provider plugin basically is responsible
for the following steps:

    * Building a url from the user given search parameters
    * Parsing the requested content from the previously built url
    * Filling in the result dictionary

There are thousend of sources one cannot support by a single tool, therefore
there is the possibility to extend libhugin youself.

You might need a japanese movie plot provider? Well you can write a plugin
yourself, its quite easy. For more information see: :ref:`providerapi`.


.. _postplugin:

Postprocessor plugins
----------------------

Postprocessor plugins are meant to *normalize* or *postprocess* the raw data
in a way specified by the user. Postprocessor plugins usually operate on result objects.

There are currently some simple postprocessor plugins available:

    * Trim
    * Customprovider

You may also want to write your own postprocessor plugin, see:
:ref:`postprocessorapi`.


.. _convplugin:

Converter plugins
-----------------------

Output converter are plugins that convert the provider delivered result to a
specific output format. It might be a xbmc nfo file, a json file, xml, html...
you name it. Currently there is a simple json and html output converter.

    * html
    * json

To implement your own output converter see:
:ref:`outputconverterapi`.


.. _analyze:

libhugin analyze
================

Currently, the analyze part's purpose is to identify missing or invalid metadata
to improve the quality of a existing movie collection.

The analyze part of the library might be extended to analyse and harvest new
information from your movie collection anytime soon. This could be done by using
different data mining algorithms and do stuff like:

    * extracting plot keywords
    * analyse similary of movies by genre, director, etc...
