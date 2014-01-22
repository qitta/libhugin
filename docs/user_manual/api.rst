.. currentmodule:: hugin.harvest.session

.. _libraryusage:

######################
Library usage tutorial
######################

Introduction
============

This tutorial describes how to use the library.


Creating a session
==================

To *communicate* with libhugin you will need to create a :class:`Session` first.

.. autoclass:: Session


Provider-, Postprocessing- and Converter plugins
------------------------------------------------

This session methods :meth:`provider_plugins`, :meth:`postprocessing_plugins` and
:meth:`converter_plugins` can be use in the same way to get the plugins name or description.
You can to it just by iterating over the provider returned list.

The following snippet demonstrates how to get the provider plugins name and
descrption:

.. code-block:: python

   session = Session()
   providers = session.provider_plugins()
   for provider in providers:
       print('{}\\n{}\\n\\n'.format(provider.name, provider.description))

Output:

::

   OFDBPerson
   Default ofdb person metadata provider.

   OFDBMovie
   Default ofdb movie metadata provider.

   TMDBPerson
   Default tmdb person metadata provider.

   TMDBMovie
   Default tmdb movie metadata provider.

   OMDBMovie
   Default omdb movie metadata provider.

.. automethod:: hugin.harvest.session.Session.provider_plugins
.. automethod:: hugin.harvest.session.Session.postprocessing_plugins
.. automethod:: hugin.harvest.session.Session.converter_plugins


Creating a query
================

After creating a :class:`Session`, you will need a query. The query represents
your *search* for a specific movie or person and may also be parametrized
individually. A query is a dictionary representing all values that are needed
for your search. The query may be build by hand, but it is recommended to use the
session :meth:`Session.create_query` method. This method returns a validated
query and its missing keys are initialized with default values.


.. automethod:: hugin.harvest.session.Session.create_query

Submiting a query
=================

After creating a session and getting a query you have to submit it by using
:meth:`Session.submit` or :meth:`Session.submit_async`. This is the point where
libhugin starts to querying the content provider to retrieve the metadata you
are searching for. The
submit method will return a list with results found.

Synchronous usage
-----------------

.. automethod:: hugin.harvest.session.Session.submit

Asynchronous usage
------------------

.. automethod:: hugin.harvest.session.Session.submit_async


Canceling and cleaning up a Session
-----------------------------------

A :class:`Session` has to be *cleaned up* after being cancelled. To do so you
will need the two methods :meth:`cancel` and :meth:`clean_up`.

.. code-block:: python

   results = []
   session = Session()
   results += session.submit_async(
       session.create_query(title='Sin', amount=100)
    )
   result += session.sunmit_async(
       session.create_query(title='Cat', amount=100)
    )

    # huh?... title Cat? ... I mean Fishcat - let's cancel.
    session.cancel()  # this sets a flag, running jobs will be finished, pending
                      # cancelled
    session.clean_up() # this will clean up everything left, like cancelling
                       # running futures and closing the internal threadpoolexecutor


.. automethod:: hugin.harvest.session.Session.cancel
.. automethod:: hugin.harvest.session.Session.clean_up
