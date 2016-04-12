import json

from dach.structs import Tenant as DictTenant
from dach.structs import Token as DictToken
from django.conf import settings
from django.utils.encoding import force_text

__backend = None


def get_backend():
    return __backend

if not getattr(settings, 'DACH_STORAGE', None):
    from dach.models import Tenant, Token

    class DatabaseBackend(object):

        def get_tenant(self, oauth_id):
            tenant = Tenant.objects.get_or_none(pk=oauth_id)
            return DictTenant(**tenant.to_dict()) if tenant else None

        def set_tenant(self, tenant):
            Tenant.objects.update_or_create(
                pk=tenant.oauth_id,
                defaults={k: v for k, v in tenant.items() if k != 'oauth_id'}
            )

        def del_tenant(self, oauth_id):
            Tenant.objects.filter(pk=oauth_id).delete()

        def get_token(self, oauth_id, scope=None):
            token = Token.objects.get_or_none(pk=oauth_id, scope=scope)
            return DictToken(**token.to_dict()) if token else None

        def set_token(self, token):
            Token.objects.update_or_create(
                pk=token.oauth_id,
                defaults={k: v for k, v in token.items() if k != 'oauth_id'}
            )

        def del_token(self, oauth_id, scope=None):
            Token.objects.filter(pk=oauth_id, scope=scope).delete()

        def del_tokens(self, oauth_id):
            Token.objects.filter(pk=oauth_id).delete()

    __backend = DatabaseBackend()

elif 'redis' in getattr(settings, 'DACH_STORAGE'):
    import redis

    class RedisBackend(object):

        def __init__(self):
            conn_params = getattr(settings, 'DACH_STORAGE')['redis']
            self.client = redis.Redis(**conn_params)

        def get_tenant(self, oauth_id):
            tenant = self.client.get('{}:tenant'.format(oauth_id))
            if tenant:
                return DictTenant(**json.loads(force_text(tenant)))
            return None

        def set_tenant(self, tenant):
            self.client.set('{}:tenant'.format(tenant.oauth_id),
                            json.dumps(tenant))

        def del_tenant(self, oauth_id):
            self.client.delete('{}:tenant'.format(oauth_id))

        def get_token(self, oauth_id, scope):
            token = self.client.get('{}:token:{}'.format(oauth_id, scope))
            if token:
                return DictToken(**json.loads(force_text(token)))
            return None

        def set_token(self, token):
            self.client.set('{}:token:{}'.format(token.oauth_id, token.scope),
                            json.dumps(token))

        def del_token(self, oauth_id, scope):
            self.client.delete('{}:token:{}'.format(oauth_id, scope))

        def del_tokens(self, oauth_id):
            for k in self.client.keys('{}:token:*'.format(oauth_id)):
                self.client.delete(k)

    __backend = RedisBackend()
