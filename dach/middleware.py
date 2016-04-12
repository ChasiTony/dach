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
            logger.debug('JWT token successfully decoded')
            issuer = unverified['iss']
            tenant = get_backend().get_tenant(issuer)
            if not tenant:
                logger.debug('no tenant found')
                return
        except:
            return
        try:
            logger.debug('tenant found for token, try to verify')
            verified = jwt.decode(token, tenant.oauth_secret)
            logger.debug('token successfully verified')
            setattr(request, 'tenant', tenant)
            logger.info('jwt token successfully validated!')
        except jwt.exceptions.ExpiredSignatureError:
            return HttpResponse(
                'Unauthorized: The JWT token has expired',
                status=401
            )
        except:
            logger.exception('JWT token verify error')
            return HttpResponse(
                'Unauthorized: The JWT token signature is invalid',
                status=401
            )
