from django.test import TestCase

from dach.shortcuts import dach_response

class ShortcutsTestCase(TestCase):

    def test_dach_response_default(self):
        res = dach_response({})
        self.assertEqual(res['Content-Type'], 'application/json')
        self.assertEqual(res['Access-Control-Allow-Origin'], '*.example.com')
        self.assertEqual(res.status_code, 200)

    def test_dach_response_custom(self):
        res = dach_response({}, status=204, content_type='application/xml',
                            cors_domains=['*.example.com', '*.example.org'])

        self.assertEqual(res['Content-Type'], 'application/xml')
        self.assertEqual(res['Access-Control-Allow-Origin'],
            '*.example.com *.example.org')
        self.assertEqual(res.status_code, 204)

    def test_dach_response_no_cors(self):
        res = dach_response({}, status=204, content_type='application/xml',
                            cors_domains=None)

        self.assertEqual(res['Content-Type'], 'application/xml')
        self.assertNotIn('Access-Control-Allow-Origin', res)
        self.assertEqual(res.status_code, 204)
