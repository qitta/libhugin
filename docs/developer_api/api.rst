.. _pluginapi:

Plugin API
==========

.. note::

   This section is for developers who wants to write plugins for libhugin. If
   you just want to use the library as it is, see :ref:`usermanual`

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
