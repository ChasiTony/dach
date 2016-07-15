User guide
==========


Storage
*******



Security
********

Access the HipChat REST API from the addon
------------------------------------------

Any call to the HipChat REST API need to be authenticated.
When a user install the addon, Dach obtains an authentication token to invoke the HipChat REST API. The authorization scope of that token depends on the scopes you have declared in ``DACH_CONFIG``.

When you need to invoke an API service, you must call the ``dach.connect.auth.get_access_token`` function to obtain a token for a given tenant.


Access the addon REST API from HipChat
--------------------------------------

Any call from HipChat client to your addon needs to be authenticated.

HipChat uses a JWT token to perform authentication.

Dach makes it very simple for you because provides a middleware to perform JWT authentication. So the only thing you need to do is to add the ``@tenant_required`` decorator to your view function and Dach, if the authentication is successful, adds a ``tenant`` property to Django HttpRequest object so you can get the tenant information directly from the request as you will do with the Django user.




Addon installation flow
***********************

Dach provides all the required services to perform the installation flow.

All you need is to include the Dach urls.py routes in your URLConf.
It publish the ``atlassian-connect.json`` addon descriptor and the install and unistall routes.

The install view function receive the security context from HipChat to talk to its API as long as information about the room and group where the addon would be installed.

Dach checks the API capabilities, gets an authentication token and stores the installation information along with the token in the choosen storage backend.

If everything goes well, Dach dispatch a ``post_install`` signal
that the addon implementor can listen to achieve post installation tasks.



For more information see the `HipChat addon installation flow <https://developer.atlassian.com/hipchat/guide/installation-flow>`_.











