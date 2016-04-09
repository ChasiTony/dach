import json
import logging
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import get_template
from django.utils.encoding import smart_text

from .models import Tenant, Token
from .utils import dotdict

logger = logging.getLogger('dach')


DESCRIPTOR = None


def get_descriptor():
    global DESCRIPTOR
    if not DESCRIPTOR:
        DESCRIPTOR = dotdict(json.loads(get_template(
            getattr(
                settings,
                'DACH_TEMPLATE_NAME',
                'atlassian-connect.json')
        ).render()))
    return DESCRIPTOR


def _generate_token(tenant, scopes):
    client_key = tenant.oauth_id
    doc = dotdict(json.loads(smart_text(tenant.capabilities_doc.read())))
    token_url = doc.capabilities.oauth2Provider.tokenUrl
    logger.debug('generate access token at %s for %s', token_url, client_key)
    payload = {
        'grant_type': 'client_credentials',
        'scope': ' '.join(scopes)
    }
    res = requests.post(
        token_url,
        data=payload,
        auth=(tenant.oauth_id, tenant.oauth_secret)
    )
    if res.status_code == 200:
        token_info = res.json()
        token, created = Token.objects.update_or_create(pk=client_key,
                                                        defaults=token_info)
        logger.info('token %s successfully',
                    'created' if created else 'updated')
        return token
    raise Exception('cannot generate access token: %s', res.status_code)


def get_and_check_capabilities(url):
    logger.debug('downloading the capabilities doc at %s', url)
    res = requests.get(url, headers={'Accept': 'application/json'})
    if res.status_code == requests.codes.ok:
        doc = dotdict(res.json())
        if doc.links.self != url:
            raise Exception('The capabilities URL doesn\'t'
                            ' match the resource self link')
        logger.info('capabilities doc downloaded')
        return doc
    raise Exception('Cannot donwload the capabilities doc: {}'
                    .format(res.status_code))


def get_access_token(tenant, scopes=None):
    scopes = scopes or get_descriptor().capabilities.hipchatApiConsumer.scopes
    client_key = tenant.oauth_id
    logger.debug('get an access token for %s', client_key)
    token = Token.objects.get_or_none(pk=client_key)
    if token:
        logger.debug('token exists for %s', client_key)
        expires = token.created + timedelta(seconds=token.expires_in)
        if expires < datetime.now():
            logger.debug('token expired for %s', client_key)
            return _generate_token(tenant, scopes)
        logger.debug('token is yet valid for %s', client_key)
        return token
    logger.debug('no token found for %s', client_key)
    return _generate_token(tenant, scopes)


def create_tenant(info, doc):
    t = Tenant()
    t.oauth_id = info['oauthId']
    t.oauth_secret = info['oauthSecret']
    t.capabilities_url = info['capabilitiesUrl']
    t.capabilities_doc.save('{}.json'.format(t.oauth_id),
                            ContentFile(json.dumps(doc)), save=False)
    t.group_id = info['groupId']
    t.room_id = info.get('roomId', None)
    return t
