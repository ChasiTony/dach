from django.dispatch import Signal


post_install = Signal(providing_args=['tenant'])
post_uninstall = Signal(providing_args=['oauth_id'])
