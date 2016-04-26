from collections import deque

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import StaticNode
from django.utils.six.moves.urllib.parse import urljoin


def lookup_dict(d, path, strict=True):
    """Utility function that allows to get a value
    from nested dictionaries through the use of dot notation.


    Args:
        d (dict): the dictionary object from which to get the value
        path (str): the path to the value expressed as key1[.key2][.key3]...
        strict (bool): if False and `path` not exists in `d` returns `None`.
        Default to `True`.

    """
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
