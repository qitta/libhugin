.. _pluginapi:

Plugin API
==========

.. note::

   This section is for developers who wants to write plugins for libhugin. If
   you just want to use the library as it is, see :ref:`usermanual`


Introduction
============


.. code-block:: sh

    hugin
    ├── analyze
    ├── core
    │   ├── cache.py
  * │   ├── converter    <-- converter plugin folder
    │   │   ├── html
    │   │   │   ├── html.py
    │   │   │   ├── html.yapsy-plugin
    │   │   │   ├── __init__.py
    │   │   │   ├── mtemplate.html
    │   │   │   └── ptemplate.html
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
    │   │       ├── __init__.py
    │   │       ├── resultdicttrimmer.py
    │   │       └── resultdicttrimmer.yapsy-plugin
  * │   ├── provider    <-- provider plugin folder
  * │   │   ├── genrefiles <-- provider subfolder with genre norm data
    │   │   │   ├── normalized_genre.dat
    │   │   │   ├── ofdb.genre
    │   │   │   ├── omdb.genre
    │   │   │   └── tmdb.genre
    │   │   ├── genrenorm.py
    │   │   ├── __init__.py
    │   │   ├── ofdb
    │   │   │   ├── __init__.py
    │   │   │   ├── ofdbcommon.py
    │   │   │   ├── ofdbmovie.py
    │   │   │   ├── ofdbmovie.yapsy-plugin
    │   │   │   ├── ofdbperson.py
    │   │   │   └── ofdbperson.yapsy-plugin
    │   │   ├── omdb
    │   │   │   ├── __init__.py
    │   │   │   ├── omdbmovie.py
    │   │   │   └── omdbmovie.yapsy-plugin
    │   │   ├── result.py
    │   │   └── tmdb
    │   │       ├── __init__.py
    │   │       ├── tmdbcommon.py
    │   │       ├── tmdbmovie.py
    │   │       ├── tmdbmovie.yapsy-plugin
    │   │       ├── tmdbperson.py
    │   │       └── tmdbperson.yapsy-plugin
    │   ├── query.py
    │   └── session.py
    ├── __init__.py
    ├── __main__.py
    └── utils
        ├── __init__.py
        ├── logutil.py
        └── stringcompare.py

.. _providerapi:

Developing a content provider plugin
------------------------------------

.. automodule:: hugin.core.provider
   :members: IProvider


Developing a movie content provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: hugin.core.provider
   :members: IMovieProvider, IMoviePictureProvider


Developing a person content provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: hugin.core.provider
   :members: IPersonProvider, IPersonPictureProvider


.. _postprocessingapi:

Developing a postprocessing plugin
----------------------------------

.. automodule:: hugin.core.provider
   :members: IPostprocessing


.. _outputconverterapi:

Developing a output converter plugin
------------------------------------

.. automodule:: hugin.core.provider
   :members: IOutputConverter
