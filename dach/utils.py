import logging
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.utils.six.moves.urllib.parse import urljoin

from .models import Tenant, Token

logger = logging.getLogger('dach')

def _get_descriptor():
    res = requests.get(urljoin(settings.DACH_BASE_URL,
                               reverse('dach_descriptor')))
    if res.status_code == requests.codes.ok:
        return res.json()
    raise Exception('cannot access the descriptor from myself')


def _generate_token(client_info, scopes):
    client_key = client_info['oauth_id']
    token_url = client_info['capabilities_doc']['capabilities']\
        ['oauth2Provider']['tokenUrl']
    logger.debug('generate access token at %s for %s', token_url, client_key)
    payload = {
        'grant_type': 'client_credentials',
        'scope': ' '.join(scopes)
    }
    res = requests.post(
        token_url,
        data=payload,
        auth=(client_info['oauth_id'], client_info['oauth_secret'])
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
        doc = res.json()
        if doc['links']['self'] != url:
            raise Exception('The capabilities URL doesn\'t'
                            ' match the resource self link')
        logger.info('capabilities doc downloaded')
        return doc
    raise Exception('Cannot donwload the capabilities doc: {}'
                    .format(res.status_code))


def get_access_token(client_info, scopes=None):
    client_key = client_info['oauth_id']
    scopes = scopes or _get_descriptor()['capabilities']['hipchatApiConsumer']\
        ['scopes']
    logger.debug('get an access token for %s', client_key)
    token = Token.objects.get_or_none(pk=client_key)
    if token:
        logger.debug('token exists for %s', client_key)
        expires = token.created + timedelta(seconds=token.expires_in)
        if expires < datetime.now():
            logger.debug('token expired for %s', client_key)
            return _generate_token(client_info, scopes)
        logger.debug('token is yet valid for %s', client_key)
        return token
    logger.debug('no token found for %s', client_key)
    return _generate_token(client_info, scopes)


def save_client_info(client_info):
    capabilities_doc = json.dumps(client_info['capabilities_doc'])
    del client_info['capabilities_doc']
    t = Tenant(client_info)
    t.capabilities_doc.save(client_info['oauth_id'],
                            ContentFile(capabilities_doc))
    return t
