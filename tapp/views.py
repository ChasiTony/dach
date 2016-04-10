import json

from django.http import HttpResponse

from dach.decorators import jwt_required


@jwt_required
def glance(request):
    g = {
        'label': {
          'type': 'html',
          'value': 'Hello World!'
        },
        'status': {
          'type': 'lozenge',
          'value': {
            'label': 'NEW',
            'type': 'error'
            }
        }
    }
    r = HttpResponse(json.dumps(g), content_type='application/json')
    r['Access-Control-Allow-Origin'] = '*'
    return r
