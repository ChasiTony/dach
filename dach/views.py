from __future__ import unicode_literals

import json
import logging

import requests

from dach.connect import get_descriptor
from dach.connect.auth import get_access_token
from dach.storage import get_backend
from dach.structs import Tenant
from django.apps import apps
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_exempt

from .signals import post_install, post_uninstall
from .utils import lookup_dict

logger = logging.getLogger(__name__)


def _get_and_check_capabilities(url):
    logger.debug('downloading the capabilities doc at %s', url)
    res = requests.get(url, headers={'Accept': 'application/json'})
    if res.status_code == requests.codes.ok:
        doc = res.json()
        if lookup_dict(doc, 'links.self') != url:
            raise Exception('The capabilities URL doesn\'t'
                            ' match the resource self link')
        logger.info('capabilities doc downloaded')
        return (lookup_dict(doc, 'capabilities.oauth2Provider.tokenUrl'),
                lookup_dict(doc, 'links.api'))

    raise Exception('Cannot donwload the capabilities doc: {}'
                    .format(res.status_code))


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
        info = json.loads(force_text(request.body))
        capabilities_url = lookup_dict(info, 'capabilitiesUrl')
        token_url, api_url = _get_and_check_capabilities(capabilities_url)
        tenant = Tenant()
        tenant.oauth_id = info['oauthId']
        tenant.oauth_secret = info['oauthSecret']
        tenant.capabilities_url = capabilities_url
        tenant.oauth_token_url = token_url
        tenant.api_url = api_url
        tenant.group_id = info['groupId']
        tenant.room_id = info.get('roomId', None)

        token = get_access_token(tenant)

        tenant.group_name = token.group_name
        get_backend().set_tenant(tenant)
        post_install.send(
            apps.get_app_config(request.resolver_match.app_name or 'dach'),
            tenant=tenant
        )
        logger.info('addon successfully installed')
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['post'])


@csrf_exempt
def uninstall(request, oauth_id):
    if request.method == 'DELETE':
        get_backend().del_tokens(oauth_id)
        get_backend().del_tenant(oauth_id)
        post_uninstall.send(
            apps.get_app_config(
                request.resolver_match.app_name or 'dach'
            ),
            oauth_id=oauth_id
        )
        logger.info('addon successfully uninstalled')
        return HttpResponse(status=204)
    return HttpResponseNotAllowed(['delete'])
