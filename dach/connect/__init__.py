import json

from django.conf import settings
from django.template.loader import get_template
from dach.utils import lookup_dict

__all__ = ['get_descriptor', 'get_api_scopes']

_DESCRIPTOR = None


def get_descriptor():
    global _DESCRIPTOR
    if not _DESCRIPTOR:
        _DESCRIPTOR = json.loads(get_template(
            getattr(
                settings,
                'DACH_TEMPLATE_NAME',
                'atlassian-connect.json')
        ).render())
    return _DESCRIPTOR


def get_api_scopes():
    return lookup_dict(get_descriptor(),
                       'capabilities.hipchatApiConsumer.scopes')
