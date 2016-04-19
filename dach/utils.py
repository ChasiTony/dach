from collections import deque

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import StaticNode
from django.utils.six.moves.urllib.parse import urljoin


def lookup_dict(d, path, strict=True):
    keys = deque(path.split('.'))
    while True:
        try:
            d = d[keys.popleft()]
        except KeyError as ke:
            if strict:
                raise ke
            return None
        except IndexError:
            return d



def abs_static(path):
    base_url = getattr(settings, 'DACH_CONFIG')['base_url']
    return urljoin(base_url, staticfiles_storage.url(path))
