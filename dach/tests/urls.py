from django.conf.urls import include, url

from .views import jwt_test_view

urlpatterns = [
    url(r'^', include('dach.urls', namespace='test', app_name='dach')),
    url(r'^jwt_test_view', jwt_test_view, name='jwt_test_view'),
]
