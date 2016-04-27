Tutorial
========

In this tutorial we will create an addon that add a `Glance <https://developer.atlassian.com/hipchat/guide/glances>`_ to a HipChat room to show information about the weather in Barcelona, Spain.

We will use the `OpenWeatherMap <https://www.openweathermap.org/>`_ API to retrieve the weather information.

You must sign in to OpenWeatherMap to obtain an api key for the purpose of this tutorial.


Setup your development environment
**********************************

.. note::

    This tutorial assumes that you have already created a virtualenv, you have installed and have created a django project called tutorial.


Requirements
------------

dach requires the following:

- Python (2.7, 3.4, 3.5)
- Django (1.8, 1.9)

dach also depends on:

- `requests <http://docs.python-requests.org/>`_ (2.7+)
- `pyjwt <https://pyjwt.readthedocs.org/>`_ (1.4.0+)

optionally, if you wish to use redis as the storage backend for the HipChat addon data, you need also:

- `redis <https://redis-py.readthedocs.org>`_ (2.10.5+)
    
.. note::

    For the purpose of this tutorial we will use sqlite as the storage backend.

To test your addon, it must be visible from the HipChat servers. In this tutorial we will use `ngrok <https://ngrok.com>`_ to create a tunnel to your django development server.


Install ngrok
-------------

Follow the `ngrok download and installation <https://ngrok.com/download>`_ guide to setup ngrok.


Start ngrok
-----------

To start ngrok types the following at the command prompt:

.. code-block:: console

    $ ngrok http 8000



Install dach
------------

You can install dach using pip:

.. code-block:: console

    $ pip install dach


To use dach you need to add it to the ``INSTALLED_APPS`` in your settings.py::

    INSTALLED_APPS = (
        ...
        'dach',
    )


HipChat needs to call your ``views`` to interacts with your addon, so you need to install the dach jwt authentication middleware to your ``MIDDLEWARE_CLASSES``: ::

    MIDDLEWARE_CLASSES = (
        ...
        'dach.middleware.HipChatJWTAuthenticationMiddleware',
    )


Then you have to add a basic dach configuration to your settings.py: ::

    DACH_CONFIG = {
        'base_url': 'https://weather.ngrok.io',
        'appconfig': {
            'weather': {
                'scopes': ['view_room']
            }
        }
    }

.. warning::

    You have to replace the ``base_url`` value with your ngrok tunnel address.


Next you can create your database:

.. code-block:: console

    $ ./manage.py migrate


Setup your weather addon django app
-----------------------------------

To create a django app for your addon you can use the ``starthip`` command.
In your project root folder type the following:

.. code-block:: console

    $ ./manage.py starthip weather


The ``starthip`` command wraps the default startapp command. In addition to the app layout created by startapp, ``starthip`` adds the following: ::

    weather/
        templates/
            weather/
                atlassian-connect.json
        urls.py


The ``urls.py`` includes the dach urls to handle the installation flow for the weather addon:

.. code-block:: python
    
    from django.conf.urls import url, include

    urlpatterns = [
        url(r'^setup/', include('dach.urls', namespace='weather',
                                app_name='weather')),
    ]


Edit your ``tutorial/urls.py`` to includes the weather app urls:

.. code-block:: python

    from django.conf.urls import url, include
    from django.contrib import admin

    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^weather/', include('weather.urls')),
    ]


Configure the weater addon
--------------------------

The ``starthip`` also created a basic ``atlassian-connect.json`` addon descriptor template file.

Take a look at this basic decriptor:

.. code-block:: html+django

    {% load dach %}
    {
      "key": "weather",
      "name": "Weather HipChat Addon",
      "description": "Description for Weather",
      "vendor": {
        "name": "Author Name",
        "url": "https://example.com"
      },
      "links": {
        "self": "{% absurl 'weather:descriptor' %}",
        "homepage": "https://example.com"
      },
      "capabilities": {
        "hipchatApiConsumer": {
          "scopes": {% scopes %}
        },
        "installable": {
          "callbackUrl": "{% absurl 'weather:install' %}"
        }
      }
    }



