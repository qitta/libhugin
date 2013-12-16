Overview
========

Libhugins modular architecture
------------------------------

.. figure:: /_static/archoverview.png
    :width: 100%


Libhugin is divided into two parts. A :ref:`core` and a :ref:`analyze` part. Both
parts are modular and may be extended by plugins.

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

The core library is responsible for fetching all the metadata.

It makes use of the following plugins types:

    * Provider Plugins
    * Postprocessing Plugins
    * Outputconverter Plugins

The modularity makes it easy to adapt hugin to your specific needs.


Providers, Converters, Postprocessing plugins
---------------------------------------------

Libhugin is all about plugins. There are three different kinds of plugins that
libhugin core makes use of.

**Provider Plulgins**

Provider Plugins are content provider that are responsible for fetching the
metadata from the web. This plugins act as ``proxy`` between a webservice  and
libhugin. A webservice might be e.g. TMDB API:

    * http://docs.themoviedb.apiary.io/

A provider plugin might also parse a html page if there is no api available.
It's up to the provider plugin. A provider plugin is responsible to tell the
core module which url to download, to parse the content and to fill in a result
object.

Tere are thousend of sources one cannot support by a single tool, therefore
there is the possibility to extend libhugin youself.

You might need a japanese movie plot provider? Well you can write a plugin
yourself, its quite easy. For more information see: ``provider.developement``.


**Postprocessing plugins**

Postprocessing plugins are meant to ``normalize`` the raw data to your specific
needs. Postprocessing plugins usually operate on result objects.

There currently some some simple postprocessing plugins available:
``postprocessing plugins``

You may also want to write your own postprocessing plugin, see ``development of
postprocessig plugins``.


**Output converter plugins**

Output converter are plugins that convert the provider delivered result to a
specific output format. It might be a xbmc nfo file, a json file, xml, html...
you name it! To implement your own output converter see: ``Writing a converter
plugin``.

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
