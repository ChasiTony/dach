import json

from dach.shortcuts import dach_response

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
    return dach_response(g)
