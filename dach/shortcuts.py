import json
from django.http import HttpResponse


def dach_response(data, content_type='application/json',
                  status=200, cors_origins=['*']):
    res = HttpResponse(json.dumps(data),
                       content_type=content_type, status=status)
    res['Access-Control-Allow-Origin'] = ' '.join(cors_origins)
    return res
