import logging

import jwt
from django.http import HttpResponse

from .storage import get_backend

logger = logging.getLogger('dach')


class HipChatJWTAuthenticationMiddleware(object):
    def process_request(self, request):
        token = request.GET.get('signed_request', None) or \
            request.META.get('HTTP_AUTHORIZATION', None)
        if not token:
            logger.debug('no JWT token found')
            return
        if token.startswith('JWT'):
            token = token[4:]
        try:
            unverified = jwt.decode(token, verify=False)
            logger.debug('jwt token decoded')
            issuer = unverified['iss']
            tenant = get_backend().get_tenant(issuer)
            if not tenant:
                logger.debug('no tenant found')
                return
        except:
            return
        try:
            logger.debug('tenant found for token, try to verify')
            jwt.decode(token, tenant.oauth_secret)
            setattr(request, 'tenant', tenant)
            logger.info('jwt token verified')
        except jwt.exceptions.ExpiredSignatureError:
            logger.info('jwt token expired')
            return HttpResponse(
                'Unauthorized: The JWT token has expired',
                status=401
            )
        except:
            logger.info('jwt token verify error')
            return HttpResponse(
                'Unauthorized: The JWT token signature is invalid',
                status=401
            )
