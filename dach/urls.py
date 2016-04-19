from django.conf.urls import url

from .views import (descriptor, install, uninstall)


urlpatterns = [
    url(r'^atlassian-connect.json$', descriptor, name='descriptor'),
    url(r'^install$', install, name='install'),
    url(r'^install/(?P<oauth_id>.*)$', uninstall, name='uninstall'),
]
