from dach import utils
from django.test import TestCase


class UtilsTestCase(TestCase):
    def test_lookup_dict(self):
        d = {
            'first': {
                'second': 'ok'
            }
        }
        self.assertEqual('ok', utils.lookup_dict(d, 'first.second'))

    def test_lookup_dict_strict(self):
        d = {
            'first': {
                'second': 'ok'
            }
        }
        with self.assertRaises(KeyError):
            utils.lookup_dict(d, 'first.third')

    def test_lookup_dict_no_strict(self):
        d = {
            'first': {
                'second': 'ok'
            }
        }
        self.assertIsNone(utils.lookup_dict(d, 'first.third', strict=False))

    def test_lookup_dict_exception(self):
        d = {
            'first': {
                'second': 'ok'
            }
        }
        with self.assertRaises(Exception):
            utils.lookup_dict(d, 'first.second.third')
