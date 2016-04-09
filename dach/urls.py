from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', homepage, name='dach_homepage'),
    url(r'^atlassian-connect.json$', descriptor, name='dach_descriptor'),
    url(r'^installable$', installable, name='dach_installable'),
    url(r'^configurable$', configurable, name='dach_configurable'),
]
