import logging
from dach.signals import post_install, post_uninstall
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_install)
def post_install_hook(sender, **kwargs):
    print(sender, kwargs)


@receiver(post_uninstall)
def post_uninstall_hook(sender, **kwargs):
    print(sender)
