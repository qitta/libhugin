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



.. toctree::
    :glob:
    :maxdepth: 1

**API Usage Example**

If you want to search for a movie, e.g. ``Sin City``:

.. code-block:: python

   from hugin import Session
   import pprint

   # First you create a sesion.
   session = Session()

   #now you have to create a query and submit it.
   query = session.create_query(title='Sin City', type='movie')

   #submit is blocking, we will retrieve a list with provider_data objects
   results = session.submit(query)

   for provider_data in results:
        pprint.pprint(provider_data)


    #the output will look like this
    Provider: OFDB <movie>{'rating': '8.74', 'countries': ['USA'], 'title': 'Sin City', 'tagline': 'Basin City, genannt Sin City, ist ein düsteres Metropolis, in dem nichts und niemand wirklich sicher ist, in dem die Gewalt allgegenwärtig ist und die', 'plot': 'Basin City, genannt Sin City, ist ein düsteres Metropolis, in dem nichts und niemand wirklich sicher ist, in dem die Gewalt allgegenwärtig ist und die Schicksale sich kreuzen. Drei Geschichten aus den dunklen Winkeln der Stadt werden hier erzählt: da ist der muskulöse Schläger Marv (Mickey Rourke), der sich auf einen beispiellosen Rachefeldzug begibt, als die einzige von ihm geliebte Frau Goldie (Jamie King) nach einer gemeinsamen Nacht von einem Killer getötet wird.; dann ist da Dwight (Clive Owen), der aus Gefühlsgründen für die eh nicht ganz so wehrlosen Prostituierten und Tänzerinnen eintritt, als ein brutaler Cop (Benicio del Toro) sie bedroht und damit selbst in immer gewalttätigere Schwierigkeiten gerät und schließlich und endlich die Story des ehrlichen Cops Hartigan (Bruce Willis), der allmählich seines Jobs müde geworden ist, aber noch einmal zur Tat schreiten muß, um die Tänzerin Nancy (Jessica Alba) zu beschützen, auf die ein Killer namens Yellow Bastard (Nick Stahl) angesetzt wurde, bereits zum zweiten Mal.\r\nBlut wird fließen...soviel ist gewiß...', 'director': ['Frank Miller', 'Robert Rodriguez', 'Quentin Tarantino'], 'actors': [{'name': 'Jessica Alba', 'role': 'Nancy Callahan'}, {'name': 'Rosario Dawson', 'role': 'Gail'}, {'name': 'Elijah Wood', 'role': 'Kevin'}, {'name': 'Bruce Willis', 'role': 'Hartigan'}, {'name': 'Benicio Del Toro', 'role': 'Jackie Boy'}, {'name': 'Michael Clarke Duncan', 'role': 'Manute'}, {'name': 'Carla Gugino', 'role': 'Lucille'}, {'name': 'Josh Hartnett', 'role': 'The Man'}, {'name': 'Michael Madsen', 'role': 'Bob'}, {'name': 'Jaime King', 'role': 'Goldie / Wendy'}, {'name': 'Brittany Murphy', 'role': 'Shellie'}, {'name': 'Clive Owen', 'role': 'Dwight McCarthy'}, {'name': 'Mickey Rourke', 'role': 'Marv'}, {'name': 'Nick Stahl', 'role': 'Roark Jr. / Yellow Bastard'}, {'name': 'Marley Shelton', 'role': 'Mordopfer [Prolog]'}, {'name': 'Arie Verveen', 'role': 'Murphy'}, {'name': 'Devon Aoki', 'role': 'Miho'}, {'name': 'Alexis Bledel', 'role': 'Becky'}, {'name': 'Jude Ciccolella', 'role': 'Liebowitz'}, {'name': 'Jason Douglas', 'role': 'Hitman'}, {'name': 'Penny Drake', 'role': 'Old Town Girl'}, {'name': 'Lauren-Elaine Edleson', 'role': 'Old Town Girl'}, {'name': 'Rick Gomez', 'role': 'Klump'}, {'name': 'Rutger Hauer', 'role': 'Cardinal Roark'}, {'name': 'Frank Miller', 'role': 'Priest'}, {'name': 'Makenzie Vega', 'role': 'Nancy, Age 11'}, {'name': 'Chris Warner', 'role': 'Bozo #3'}, {'name': 'Katherine Willis', 'role': 'Powers Boothe'}, {'name': 'Powers Boothe', 'role': 'Senator Roark'}, {'name': 'Jeffrey J. Dashnaw', 'role': 'Motorcycle Cop'}, {'name': 'Tommy Flanagan', 'role': 'Brian'}, {'name': 'Nicky Katt', 'role': 'Stuka'}, {'name': 'Clark Middleton', 'role': 'Schutz'}, {'name': 'Ethan Rains', 'role': 'Bozo #4'}, {'name': 'Lisa Marie Newmyer', 'role': 'Tammy'}, {'name': 'Nick Offerman', 'role': 'Shlubb'}, {'name': 'Patricia Vonne', 'role': 'Dallas'}, {'name': 'Danny Wynands', 'role': 'Big Mercenary'}, {'name': 'Amanda Phillips', 'role': 'Girl'}, {'name': 'Emmy Robbin', 'role': 'Old Town Girl'}, {'name': 'Kelley Robins', 'role': "Ol' Town Girl"}, {'name': 'Texas', 'role': 'Old Town Girl'}, {'name': 'Greg Ingram', 'role': ''}, {'name': 'Ethan Maniquis', 'role': ''}, {'name': 'Jason McDonald', 'role': ''}, {'name': 'Tommy Nix', 'role': ''}, {'name': 'Jeff Schwan', 'role': ''}, {'name': 'Scott Teeters', 'role': ''}, {'name': 'Ken Thomas', 'role': ''}, {'name': 'Cara D. Briggs', 'role': ''}, {'name': 'Jesse De Luna', 'role': ''}, {'name': 'Christina Frankenfield', 'role': ''}, {'name': 'David H. Hickey', 'role': ''}, {'name': 'Evelyn Hurley', 'role': ''}, {'name': 'Helen Kirk', 'role': ''}, {'name': 'John McLeod', 'role': ''}, {'name': 'Marco Perella', 'role': ''}, {'name': 'Sam Ray', 'role': ''}, {'name': 'Randal Reeder', 'role': ''}, {'name': 'David Alex Ruiz', 'role': ''}, {'name': 'Ryan Rutledge', 'role': ''}, {'name': 'Korey Simeone', 'role': ''}, {'name': 'Paul T. Taylor', 'role': ''}, {'name': 'Rico Torres', 'role': ''}, {'name': 'Shaun Wainwright-Branigan', 'role': ''}, {'name': 'J.D. Young', 'role': ''}, {'name': 'Babs George', 'role': ''}, {'name': 'Ron Hayden', 'role': ''}, {'name': 'Lucina Paquet', 'role': ''}, {'name': 'Charissa Allen', 'role': ''}, {'name': 'Jessica Hale', 'role': ''}, {'name': 'Sammy Harte', 'role': ''}, {'name': 'Ashley Moore', 'role': ''}], 'year': '2005', 'imdbid': 'tt0401792', 'poster': 'http://img.ofdb.de/film/72/72886.jpg', 'genre': ['Action', 'Thriller'], 'writer': [{'name': 'Frank Miller'}], 'original_title': 'Sin City'}
    Provider: TMDB <movie>{'rating': 6.6, 'providerid': 187, 'countries': ['United States of America'], 'title': 'Sin City', 'plot': "Sin City is a neo-noir crime thriller based on Frank Miller's graphic novel series of the same name.The film is primarily based on three of Miller's works: The Hard Goodbye, about a man who embarks on a brutal rampage in search of his one-time sweetheart's killer; The Big Fat Kill, which focuses on a street war between a group of prostitutes and a group of mercenaries; and That Yellow Bastard, which follows an aging police officer who protects a young woman from a grotesquely disfigured serial killer.", 'imdbid': 'tt0401792', 'vote_count': 544, 'studios': ['Miramax Films', 'Dimension Films', 'Troublemaker Studios'], 'year': '2005', 'fanart': [], 'poster': [], 'genre': ['Action', 'Crime', 'Thriller'], 'runtime': 124, 'original_title': 'Sin City', 'collection': {'name': 'Sin City Collection', 'id': 135179, 'poster_path': '/fKX37CixhzX4YUnauttvfbRkUTQ.jpg', 'backdrop_path': '/qs200GlvLNIQKUns6AIeLcJWtPT.jpg'}}
    Provider: OMDB <movie>{'plot': ['A film that explores the dark and miserable town', ' Basin City', ' and tells the story of three different people', ' all caught up in violent corruption.'], 'title': 'Sin City', 'rating': '8.2', 'director': ['Frank Miller', ' Robert Rodriguez'], 'vote_count': '463730', 'actors': ['Mickey Rourke', ' Clive Owen', ' Bruce Willis', ' Jessica Alba'], 'year': '2005', 'imdbid': 'tt0401792', 'genre': ['Crime', ' Thriller'], 'writer': ['Frank Miller'], 'runtime': ['2 h 27 min'], 'poster': (None, 'http://ia.media-imdb.com/images/M/MV5BMTI2NjUyMDUyMV5BMl5BanBnXkFtZTcwMzU0OTkyMQ@@._V1_SX300.jpg')}


You can also use the ``submit_async`` method on submit, this one will not block,
it will return a future object :mod:`concurrent.futures`.


Currently the API supports searching for:

    * movie by title and year
    * movie imdbid
    * person by name


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
