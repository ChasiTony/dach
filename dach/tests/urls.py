from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('dach.urls')),
]
