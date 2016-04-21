import os
import shutil

import six
from django.core.management import call_command
from django.test import TestCase


class CommandTestCase(TestCase):

    def test_command(self):
        out = six.StringIO()
        call_command('starthip', 'addon', stdout=out)
        self.assertIn('application addon generated', out.getvalue())

    def tearDown(self):
        root_path = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
        app_dir = os.path.join(root_path, 'addon')
        if os.path.exists(app_dir):
            shutil.rmtree(app_dir)
