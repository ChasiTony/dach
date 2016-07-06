Tutorial
========

In this tutorial we will create an addon that add an "Hello World" `Glance <https://developer.atlassian.com/hipchat/guide/glances>`_ to an HipChat room.



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
        'base_url': 'https://helloworld.ngrok.io',
        'appconfig': {
            'helloworld': {
                'scopes': ['view_room']
            }
        }
    }

.. warning::

    You have to replace the ``base_url`` value with your ngrok tunnel address.


Next you can create your database:

.. code-block:: console

    $ ./manage.py migrate


Setup your helloworld addon django app
--------------------------------------

To create a django app for your addon you can use the ``starthip`` command.
In your project root folder type the following:

.. code-block:: console

    $ ./manage.py starthip helloworld


The ``starthip`` command wraps the default startapp command. In addition to the app layout created by startapp, ``starthip`` adds the following: ::

    helloworld/
        templates/
            helloworld/
                atlassian-connect.json
        urls.py


The ``urls.py`` includes the dach urls to handle the installation flow for the helloworld addon:

.. code-block:: python
    
    from django.conf.urls import url, include

    urlpatterns = [
        url(r'^setup/', include('dach.urls', namespace='helloworld',
                                app_name='helloworld')),
    ]


Edit your ``tutorial/urls.py`` to includes the helloworld app urls:

.. code-block:: python

    from django.conf.urls import url, include
    from django.contrib import admin

    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^helloworld/', include('helloworld.urls')),
    ]


Configure the helloworld addon
------------------------------

The ``starthip`` also created a basic ``atlassian-connect.json`` addon descriptor template file.

Take a look at this basic decriptor:

.. code-block:: html+django

    {% load dach %}
    {
      "key": "helloworld",
      "name": "Helloworld HipChat Addon",
      "description": "Description for Helloworld",
      "vendor": {
        "name": "Author Name",
        "url": "https://example.com"
      },
      "links": {
        "self": "{% absurl 'helloworld:descriptor' %}",
        "homepage": "https://example.com"
      },
      "capabilities": {
        "hipchatApiConsumer": {
          "scopes": {% scopes %}
        },
        "installable": {
          "callbackUrl": "{% absurl 'helloworld:install' %}"
        }
      }
    }

It loads the dach template tags library and use the ``absurl`` tag to 
render the ``atlassian-connect.json`` addon descriptor with absolute urls.
 

Now it's time to add the glance to your addon descriptor:


.. code-block:: html+django
    :emphasize-lines: 19-31

    {% load dach %}
    {
      "key": "helloworld",
      "name": "Helloworld HipChat Addon",
      "description": "Description for Helloworld",
      "vendor": {
        "name": "Author Name",
        "url": "https://example.com"
      },
      "links": {
        "self": "{% absurl 'helloworld:descriptor' %}",
        "homepage": "https://example.com"
      },
      "capabilities": {
        "hipchatApiConsumer": {
          "scopes": {% scopes %}
        },
      },
      "glance": [
        {
          "icon": {
            "url": "{% absstatic 'img/helloworld.svg' %}",
            "url@2x": "{% absstatic 'img/helloworld.svg' %}"
          },
          "key": "helloworld.glance",
           "name": {
              "value": "Hello world"
           },
           "queryUrl": "{% absurl 'query_glance' %}"
        }
      ],
      "installable": {
        "callbackUrl": "{% absurl 'helloworld:install' %}"
      }
    }


Add a view to your URLConf
--------------------------

Next you need to modify the ``urls.py`` of your addon app to allow HipChat to query for the data of your Glance.

.. code-block:: python
    
    from django.conf.urls import url, include

    from . import views

    urlpatterns = [
        url(r'^setup/', include('dach.urls', namespace='helloworld',
                                app_name='helloworld')),
        url(r'^query_glance$', views.query_glance, name='query_glance'),
    ]


Write your glance query view
----------------------------

Finally you have to write the view method to provide data to HipChat for your Glance.


.. code-block:: python

    from dach.decorators import tenant_required
    from dach.shortcuts import dach_response
    from dach.utils import abs_static

    @tenant_required
    def glance(request):
        url = abs_static('img/thumbsup.svg')
        glance_data = {
            'label': {
                'type': 'html',
                'value': 'Hello world'
            },
            'status': {
                'type': 'icon',
                'value': {
                    'url': url,
                    'url@2x': url
                }
            }
        }
        return dach_response(glance_data)

The ``@tenant_required`` decorator check for an authenticated tenant.
The ``abs_static`` function generate an absolute url for a static asset.
Finally the ``dach_response`` create a response object with the right content type.


