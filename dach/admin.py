from django.contrib import admin
from .models import Tenant, Token

admin.site.register(Tenant)
admin.site.register(Token)
