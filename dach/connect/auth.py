import logging
from datetime import datetime, timedelta
import time

import requests
from dach.storage import get_backend
from dach.structs import Token


logger = logging.getLogger(__name__)


def get_access_token(tenant):

    def _generate_token():
        logger.debug('generate access token at %s for %s',
                     tenant.oauth_token_url, tenant.oauth_id)
        payload = {
            'grant_type': 'client_credentials',
            'scope': ' '.join(tenant.scopes.split('|'))
        }
        res = requests.post(
            tenant.oauth_token_url,
            data=payload,
            auth=(tenant.oauth_id, tenant.oauth_secret)
        )
        if res.status_code == 200:
            token_info = res.json()
            token = Token(oauth_id=tenant.oauth_id, **token_info)
            token.created = time.time()
            token.scope = '|'.join(token.scope.split(' '))
            get_backend().set_token(token)
            return token
        raise Exception('cannot generate access token: %s', res.status_code)

    token = get_backend().get_token(tenant.oauth_id, tenant.scopes)
    if token:
        logger.debug('token exists for %s', tenant.oauth_id)
        expires = datetime.fromtimestamp(float(token.created)) + timedelta(seconds=token.expires_in)
        if expires < datetime.now():
            logger.debug('token expired for %s', tenant.oauth_id)
            return _generate_token()
        logger.debug('token is yet valid for %s', tenant.oauth_id)
        return token
    logger.debug('no token found for %s', tenant.oauth_id)
    return _generate_token()
