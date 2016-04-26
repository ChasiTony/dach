from django.dispatch import Signal


post_install = Signal(providing_args=['tenant'])
"""Dispatched when the installation flow of an HipChat integration
is successfully completed.

Arguments sent with this signal are:

**sender**

The :class:`~django.apps.AppConfig` of the app the install view belongs to

**tenant**

The tenant instance for this integration installation"""

post_uninstall = Signal(providing_args=['oauth_id'])
"""Dispatched when the uninstallation flow of an HipChat integration
is successfully completed.
Arguments sent with this signal are:

**sender**

The :class:`~django.apps.AppConfig` of the app the install view belongs to

**oauth_id**

The oauth_id of the uninstalled instance"""
