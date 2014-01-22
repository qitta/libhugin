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
kind of movie metadata. The library is divided into two parts, the :ref:`harvest`
part, which is responsible for fetching all the metadata and the :ref:`analyze`
part for analyzing a existing movie collection to improve its quality by
detecting missing metadata or extracting new information from the existing
collection.

In short - libhugin's goal is to be fast and flexible by providing a *simple and
extensible* library which is also suitable for scripting tasks.

For a short demo - let's search for the movie **Sin City**:

.. code-block:: python

   >>> from hugin.harvest import Session

   >>> session = Session() # Create a sesion.
   >>> query = session.create_query(title='Sin City') # Create a query.
   >>> results = session.submit(query) # Search it!

   >>> print(results)

   [<TMDBMovie <picture, movie> : Sin City (2005)>,
   <OFDBMovie <movie> : Sin City (2005)>,
   <OMDBMovie <movie> : Sin City (2005)>]


Easy as pie - isn't it?

The same way you can search for person metadata. It is also possible to search
by *imdb* movie id. For more information about library usage see:
:ref:`libraryusage`.

For simple scripting task or console usage there is also a minmalistic console
tool available, see: :ref:`cmdtool`.



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
    :maxdepth: 2

    developer_api/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
