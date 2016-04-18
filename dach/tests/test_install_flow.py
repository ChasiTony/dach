import base64
import json

import responses
import six
from dach.signals import post_install, post_uninstall
from dach.storage import get_backend
from dach.structs import Tenant, Token
from django.apps import apps
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import force_text

if six.PY3:
    from unittest.mock import MagicMock
else:
    from mock import MagicMock


class InstallFlowTestCase(TestCase):

    def method_not_allowed(self, url, allowed):
        methods = ('get', 'post', 'head', 'options',
                   'put', 'patch', 'delete')
        for method_name in filter(lambda x: x != allowed, methods):
            method = getattr(self.client, method_name)
            res = method(url)
            self.assertEqual(res.status_code, 405)

    def test_descriptor(self):
        response = self.client.get(reverse('test:dach_descriptor'))
        self.assertEqual(response.status_code, 200)

    def test_descriptor_http_method_not_allowed(self):
        self.method_not_allowed(reverse('test:dach_descriptor'), 'get')

    @responses.activate
    def test_install(self):
        handler = MagicMock()
        post_install.connect(handler)

        def token_request_callback(request):
            auth = request.headers['Authorization']
            auth = force_text(base64.b64decode(auth[6:]))
            auth = auth.split(':')
            payload = six.moves.urllib_parse.parse_qs(request.body)
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
                'self': 'http://someurl.com/capabilities',
                'api': 'http://someurl.com/api'
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
            reverse('test:dach_installable'),
            data=json.dumps(post_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)

        tenant = get_backend().get_tenant('my_oauth_id')
        token = get_backend().get_token('my_oauth_id', 'scope1|scope2')
        self.assertIsNotNone(tenant)
        self.assertIsNotNone(token)
        self.assertEqual(tenant.oauth_secret, 'my_oauth_secret')
        self.assertEqual(tenant.group_id, 1)
        self.assertEqual(tenant.group_name, 'test_group')
        self.assertEqual(tenant.room_id, 2)
        self.assertEqual(tenant.capabilities_url,
                         'http://someurl.com/capabilities')
        self.assertEqual(tenant.api_url,
                         'http://someurl.com/api')
        # self.assertEqual(force_text(tenant.capabilities_doc.read()),
        #                  json.dumps(capabilities_response))
        self.assertEqual(token.group_id, 1)
        self.assertEqual(token.group_name, 'test_group')
        self.assertEqual(token.access_token, 'my access token')
        self.assertEqual(token.expires_in, 3600)
        self.assertEqual(token.scope, 'scope1|scope2')
        self.assertEqual(token.token_type, 'bearer')

        handler.assert_called_once_with(
            signal=post_install,
            sender=apps.get_app_config('dach'),
            tenant=tenant
        )

    def test_install_http_method_not_allowed(self):
        self.method_not_allowed(reverse('test:dach_installable'), 'post')

    def test_uninstall(self):
        handler = MagicMock()
        post_uninstall.connect(handler)
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
        res = self.client.delete(reverse('test:dach_uninstall',
                                         args=['my_oauth_id']))
        self.assertEqual(res.status_code, 204)
        self.assertIsNone(get_backend().get_tenant('my_oauth_id'))
        self.assertIsNone(get_backend().get_token('my_oauth_id',
                                                  'scope1|scope2'))
        handler.assert_called_once_with(
            signal=post_uninstall,
            sender=apps.get_app_config('dach'),
            oauth_id='my_oauth_id'
        )

    def test_uninstall_http_method_not_allowed(self):
        self.method_not_allowed(reverse('test:dach_uninstall', args=['test']),
                                'delete')
