import base64
import json
from unittest.mock import MagicMock

import responses
from dach.models import Tenant, Token
from dach.signals import post_install
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import smart_text
from six.moves.urllib_parse import parse_qs


class InstallTestCase(TestCase):

    def test_descriptor(self):
        response = self.client.get(reverse('dach_descriptor'))
        self.assertEqual(response.status_code, 200)

    def test_descriptor_http_method_not_allowed(self):
        for methodname in ('post', 'head', 'options',
                           'put', 'patch', 'delete'):
            method = getattr(self.client, methodname)
            res = method(reverse('dach_descriptor'))
            self.assertEqual(res.status_code, 405)

    @responses.activate
    def test_install(self):
        handler = MagicMock()
        post_install.connect(handler)

        def token_request_callback(request):
            auth = request.headers['Authorization']
            auth = smart_text(base64.b64decode(auth[6:]))
            auth = auth.split(':')
            payload = parse_qs(request.body)
            self.assertEqual(auth[0], 'my_oauth_id')
            self.assertEqual(auth[1], 'my_oauth_secret')
            self.assertIn('grant_type', payload)
            self.assertIn('scope', payload)
            return (200, {'Content_Type': 'application/json'},
                    json.dumps(token_response))

        post_data = {
            'oauthId': 'my_oauth_id',
            'oauthSecret': 'my_oauth_secret',
            'capabilitiesUrl': 'http://someurl.com/capabilities',
            'groupId': 1,
            'roomId': 2
        }
        capabilities_response = {
            'links': {
                'self': 'http://someurl.com/capabilities'
            },
            'capabilities': {
                'oauth2Provider': {
                    'tokenUrl': 'http://someurl.com/token'
                }
            }
        }
        token_response = {
            'access_token': 'my access token',
            'expires_in': 3600,
            'group_name': 'test_group',
            'token_type': 'bearer',
            'scope': 'scope1 scope2',
            'group_id': 1
        }
        responses.add(
            responses.GET,
            'http://someurl.com/capabilities',
            body=json.dumps(capabilities_response),
            content_type='application/json',
            status=200
        )
        responses.add_callback(
            responses.POST,
            'http://someurl.com/token',
            callback=token_request_callback
        )

        response = self.client.post(
            reverse('dach_installable'),
            data=json.dumps(post_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

        tenant = Tenant.objects.get_or_none(pk='my_oauth_id')
        token = Token.objects.get_or_none(pk='my_oauth_id')
        self.assertIsNotNone(tenant)
        self.assertIsNotNone(token)
        self.assertEqual(tenant.oauth_secret, 'my_oauth_secret')
        self.assertEqual(tenant.group_id, 1)
        self.assertEqual(tenant.group_name, 'test_group')
        self.assertEqual(tenant.room_id, 2)
        self.assertEqual(tenant.capabilities_url,
                         'http://someurl.com/capabilities')
        self.assertEqual(smart_text(tenant.capabilities_doc.read()),
                         json.dumps(capabilities_response))
        self.assertEqual(token.group_id, 1)
        self.assertEqual(token.group_name, 'test_group')
        self.assertEqual(token.access_token, 'my access token')
        self.assertEqual(token.expires_in, 3600)
        self.assertEqual(token.scope, 'scope1 scope2')
        self.assertEqual(token.token_type, 'bearer')

        handler.assert_called_once_with(
            signal=post_install,
            sender='dach.views',
            tenant=tenant
        )

    def test_install_http_method_not_allowed(self):
        for methodname in ('get', 'head', 'options', 'put', 'patch', 'delete'):
            method = getattr(self.client, methodname)
            res = method(reverse('dach_installable'))
            self.assertEqual(res.status_code, 405)

    def test_uninstall(self):
        tenant_data = {
            'oauth_id': 'my_oauth_id',
            'oauth_secret': 'my_oauth_secret',
            'capabilities_url': 'http://someurl.com/capabilities',
            'group_id': 1,
            'room_id': 2
        }
        token_data = {
            'access_token': 'my access token',
            'expires_in': 3600,
            'group_name': 'test_group',
            'token_type': 'bearer',
            'scope': 'scope1 scope2',
            'group_id': 1
        }
        Tenant.objects.create(**tenant_data)
        Token.objects.create(**token_data)
        res = self.client.delete(reverse('dach_uninstall',
                                         args=['my_oauth_id']))
        self.assertEqual(res.status_code, 204)
        self.assertEqual(Tenant.objects.filter(pk='my_oauth_id').count(), 0)
        self.assertEqual(Token.objects.filter(pk='my_oauth_id').count(), 0)

    def test_uninstall_http_method_not_allowed(self):
        for methodname in ('get', 'post', 'head', 'options', 'put', 'patch'):
            method = getattr(self.client, methodname)
            res = method(reverse('dach_uninstall', args=['test']))
            self.assertEqual(res.status_code, 405)
