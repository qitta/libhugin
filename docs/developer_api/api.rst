.. currentmodule:: hugin.core.provider

.. _pluginapi:

############
Introduction
############


.. note::

   This section is for developers who wants to write plugins for libhugin. If
   you just want to use the library as it is, see :ref:`usermanual`


To write plugins for libhugin you need to get to know the project structure
first. Here is a overview of the structure where provider, prostprocessing and
converter plugins are located. The overview is shortened.

libhuin project structure
=========================

.. code-block:: sh

    hugin
    ├── analyze
    ├── core
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
  * │   ├── postprocessing   <-- postprocessing plugin folder
    │   │   ├── composer
    │   │   │   ├── composer.py
    │   │   │   ├── composer.yapsy-plugin
    │   │   │   └── __init__.py
    │   │   └── resultdicttrimmer
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

In the following snippet, you see examplar the converter dicionary. No matter if
a content provider, output converter or postprocessing plugin the structure is
like seen in the following example:

::

    hugin
    ├── core
    │   ├── cache.py
    │   ├── converter           <-- converter plugin folder.
    │   │   └── json            <-- json plugin, a module containing the implementation and a yapsy plugin description file.
    │   │       ├── __init__.py
    │   │       ├── json.py
    │   │       └── json.yapsy-plugin


The plugin itself is located in a folder with a __init__.py to make it act as a
module. The plugin itself in this case is the json.py file, in this case this is
a class inheriting from the postprocessing interface implementing the needed
methods. The *'*.yapsy-plugin'* file is a description file that should name and
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

.. autoclass:: hugin.core.provider.IMovieProvider

IPersonProvider
===============

.. autoclass:: hugin.core.provider.IPersonProvider


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

.. automethod:: hugin.core.provider.IProvider.build_url

The parse reponse method
========================

.. automethod:: hugin.core.provider.IProvider.parse_response


.. _postprocessingapi:

##################################
Developing a postprocessing plugin
##################################

All postprocessing plugins have to inherit from :class:`IPostprocessing` and
implement the following method:

.. automethod:: hugin.core.provider.IPostprocessing.process


.. _outputconverterapi:

####################################
Developing a output converter plugin
####################################

All output converter plugins have to inherit from :class:`IOutputConverter` and
im implement the following method:

.. automethod:: hugin.core.provider.IOutputConverter.convert
