from django.contrib import admin
from django.conf import settings


if not getattr(settings, 'DACH_CONFIG').get('storage', None):
    from .models import DachObject

    admin.site.register(DachObject)
