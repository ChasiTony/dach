import json

from django.conf import settings
from django.http import HttpResponse

_cors_domains = getattr(settings, 'DACH_CONFIG').get('cors_domains', None)


def dach_response(data, content_type='application/json',
                  status=200, cors_domains=_cors_domains):
    res = HttpResponse(json.dumps(data),
                       content_type=content_type, status=status)
    if cors_domains:
        res['Access-Control-Allow-Origin'] = ' '.join(cors_domains)
    return res
