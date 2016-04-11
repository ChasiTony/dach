from __future__ import unicode_literals

import json
import logging

from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt

from .connect import (get_descriptor, create_tenant, get_access_token,
                      get_and_check_capabilities)
from .models import Tenant, Token
from .signals import post_install, post_uninstall
from .utils import dotdict


logger = logging.getLogger('dach')


def descriptor(request):
    if request.method == 'GET':
        return HttpResponse(
            json.dumps(get_descriptor()),
            content_type='application/json'
        )
    return HttpResponseNotAllowed(['get'])


@csrf_exempt
def install(request):
    if request.method == 'POST':
        info = dotdict(json.loads(smart_text(request.body)))
        doc = get_and_check_capabilities(info.capabilitiesUrl)
        tenant = create_tenant(info, doc)
        token = get_access_token(tenant)
        tenant.group_name = token.group_name
        tenant.save()
        post_install.send(__name__, tenant=tenant)
        logger.info('addon successfully installed')
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['post'])


@csrf_exempt
def uninstall(request, oauth_id):
    if request.method == 'DELETE':
        Token.objects.filter(pk=oauth_id).delete()
        Tenant.objects.filter(pk=oauth_id).delete()
        post_uninstall.send(__name__)
        logger.info('addon successfully uninstalled')
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['delete'])
