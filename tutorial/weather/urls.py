from django.conf.urls import url, include

urlpatterns = [
    url(r'^setup/', include('dach.urls', namespace='weather',
                            app_name='weather')),
]
