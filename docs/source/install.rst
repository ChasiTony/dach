Installation
============


Requirements
************

dach requires the following:

- Python (2.7, 3.4, 3.5)
- Django (1.8, 1.9)

dach also depends on:

- `requests <http://docs.python-requests.org/>`_ (2.7+)
- `pyjwt <https://pyjwt.readthedocs.org/>`_ (1.4.0+)

optionally, if you wish to use redis as a storage backend for the HipChat integration data, you need also:

- `redis <https://redis-py.readthedocs.org>`_ (2.10.5+)

Installing dach
***************

Install ``dach`` using pip::
	
	pip install dach


Add ``dach`` to your ``INSTALLED_APPS`` in your settings.py::

	INSTALLED_APPS = (
		...
		'dach',
	)


Add the dach jwt authentication middleware to your ``MIDDLEWARE_CLASSES`` in your settings.py::

	MIDDLEWARE_CLASSES = (
		...
		'dach.middleware.HipChatJWTAuthenticationMiddleware',
	)

