from django.contrib import admin
from django.conf import settings


if not getattr(settings, 'DACH_CONFIG').get('storage', None):
    from .models import Tenant, Token

    admin.site.register(Tenant)
    admin.site.register(Token)
