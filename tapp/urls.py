from django.conf.urls import url

from .views import glance

urlpatterns = [
    url(r'^glance$', glance, name='tapp_glance'),
]
