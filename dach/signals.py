from django.dispatch import Signal


post_install = Signal(providing_args=['tenant'])
post_uninstall = Signal()
