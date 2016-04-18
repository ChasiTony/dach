import os
import string

from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from importlib import import_module


DESCRIPTOR_TEMPLATE="""
{% load dach %}
{
  "key": "$app_name",
  "name": "$cap_app_name HipChat Addon",
  "description": "Description for $cap_app_name",
  "vendor": {
    "name": "Author Name",
    "url": "https://example.com"
  },
  "links": {
    "self": "{% absurl 'dach_descriptor' %}",
    "homepage": "https://example.com"
  },
  "capabilities": {
    "hipchatApiConsumer": {
      "scopes": [
      ]
    },
    "installable": {
      "callbackUrl": "{% absurl 'dach_installable' %}"
    }
  }
}
"""


class Command(TemplateCommand):
    help = ("Creates a Dach Addon app directory structure for the given app "
            "name in the current directory or optionally in the given "
            "directory.")
    missing_args_message = "You must provide an addon name."

    def handle(self, **options):
        app_name, target = options.pop('name'), options.pop('directory')
        self.validate_name(app_name, "app")

        try:
            import_module(app_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing "
                               "Python module and cannot be used as an app "
                               "name. Please try another name." % app_name)

        super(Command, self).handle('app', app_name, target, **options)
        if target is None:
            app_dir = os.path.join(os.getcwd(), app_name)
        else:
            app_dir = os.path.abspath(os.path.expanduser(target))

        template_dir = os.path.join(app_dir, 'templates', app_name)
        os.mkdirs(template_dir)
        t = string.Template(DESCRIPTOR_TEMPLATE)
        descriptor = t.substitute(app_name=app_name,
                                  cap_app_name=app_name.capitalize())
        descriptor_name = os.path.join(template_dir, 'atlassian-connect.json')
        with open(descriptor_name, 'w') as f:
            f.write(descriptor)
