from django.conf.urls import url

from .views import (descriptor, install, uninstall)


urlpatterns = [
    url(r'^atlassian-connect.json$', descriptor, name='dach_descriptor'),
    url(r'^install$', install, name='dach_installable'),
    url(r'^install/(?P<oauth_id>.*)$', uninstall, name='dach_uninstall'),
]
