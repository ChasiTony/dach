from dach.structs import Tenant, Token
from django.conf import settings
from django.utils.encoding import force_text

__backend = None


def get_backend():
    return __backend

if not getattr(settings, 'DACH_STORAGE', None):
    from dach.models import Tenant as DbTenant, Token as DbToken

    class DatabaseBackend(object):

        def get_tenant(self, oauth_id):
            tenant = DbTenant.objects.get_or_none(pk=oauth_id)
            return Tenant(**tenant.to_dict()) if tenant else None

        def set_tenant(self, tenant):
            DbTenant.objects.update_or_create(
                pk=tenant.oauth_id,
                defaults={k: v for k, v in tenant.items() if k != 'oauth_id'}
            )

        def del_tenant(self, oauth_id):
            DbTenant.objects.filter(pk=oauth_id).delete()

        def get_token(self, oauth_id, scope=None):
            token = DbToken.objects.get_or_none(pk=oauth_id, scope=scope)
            return Token(**token.to_dict()) if token else None

        def set_token(self, token):
            DbToken.objects.update_or_create(
                pk=token.oauth_id,
                defaults={k: v for k, v in token.items() if k != 'oauth_id'}
            )

        def del_token(self, oauth_id, scope=None):
            DbToken.objects.filter(pk=oauth_id, scope=scope).delete()

        def del_tokens(self, oauth_id):
            DbToken.objects.filter(pk=oauth_id).delete()

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
                return Tenant.from_json(force_text(tenant))
            return None

        def set_tenant(self, tenant):
            self.client.set('{}:tenant'.format(tenant.oauth_id),
                            tenant.json())

        def del_tenant(self, oauth_id):
            self.client.delete('{}:tenant'.format(oauth_id))

        def get_token(self, oauth_id, scope):
            token = self.client.get('{}:token:{}'.format(oauth_id, scope))
            if token:
                return Token.from_json(force_text(token))
            return None

        def set_token(self, token):
            self.client.set('{}:token:{}'.format(token.oauth_id, token.scope),
                            token.json())

        def del_token(self, oauth_id, scope):
            self.client.delete('{}:token:{}'.format(oauth_id, scope))

        def del_tokens(self, oauth_id):
            for k in self.client.keys('{}:token:*'.format(oauth_id)):
                self.client.delete(k)

    __backend = RedisBackend()
