from time import time

import jwt
from dach.storage import get_backend
from dach.structs import Tenant, Token
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import force_text
from six.moves.urllib_parse import quote_plus


class JWTTestCase(TestCase):

    def setUp(self):
        tenant_data = {
            'oauth_id': 'my_oauth_id',
            'oauth_secret': 'my_oauth_secret',
            'capabilities_url': 'http://someurl.com/capabilities',
            'group_id': 1,
            'room_id': 2
        }
        token_data = {
            'oauth_id': 'my_oauth_id',
            'access_token': 'my access token',
            'expires_in': 3600,
            'group_name': 'test_group',
            'token_type': 'bearer',
            'scope': 'scope1|scope2',
            'group_id': 1
        }
        get_backend().set_tenant(Tenant(**tenant_data))
        get_backend().set_token(Token(**token_data))

    def test_valid_jwt_querystring(self):
        payload = {
            'iss': 'my_oauth_id',
            'exp': time() + 3600
        }
        encoded = jwt.encode(payload, 'my_oauth_secret')
        url = '{}?signed_request={}'.format(reverse('jwt_test_view'),
                                            quote_plus(encoded))
        res = self.client.get(url)
        self.assertEqual(res.status_code, 204)

    def test_valid_jwt_header(self):
        payload = {
            'iss': 'my_oauth_id',
            'exp': time() + 3600
        }
        encoded = jwt.encode(payload, 'my_oauth_secret')
        res = self.client.get(reverse('jwt_test_view'),
            HTTP_AUTHORIZATION='JWT {}'.format(force_text(encoded)))
        self.assertEqual(res.status_code, 204)

    def test_jwt_invalid_signature(self):
        payload = {
            'iss': 'my_oauth_id',
            'exp': time() + 3600
        }
        encoded = jwt.encode(payload, 'no_valid_oauth_secret')
        res = self.client.get(reverse('jwt_test_view'),
            HTTP_AUTHORIZATION='JWT {}'.format(force_text(encoded)))
        self.assertEqual(res.status_code, 401)
        self.assertEqual('Unauthorized: The JWT token signature is invalid',
                         force_text(res.content))

    def test_jwt_token_expired(self):
        payload = {
            'iss': 'my_oauth_id',
            'exp': time() - 6600
        }
        encoded = jwt.encode(payload, 'my_oauth_secret')
        res = self.client.get(reverse('jwt_test_view'),
            HTTP_AUTHORIZATION='JWT {}'.format(force_text(encoded)))
        self.assertEqual(res.status_code, 401)
        self.assertEqual('Unauthorized: The JWT token has expired',
                         force_text(res.content))
