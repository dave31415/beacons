Logger App
======

Python: 2.7.3

Flask

Install
-------

$ sqlite3 /tmp/beacon_log.db < schema.sql

$ python

    >>> from logger import init_db

    >>> init_db()

$ python logger.py

 * Running on http://localhost:7979/
