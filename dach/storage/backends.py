from django.conf import settings

__backend = None


def get_backend():
    return __backend


def _key(client_id, key):
    return '{}:{}'.format(client_id, key)


class AbstractBackend(object):
    def get(self, client_id, key):
        raise NotImplementedError()

    def set(self, client_id, key, value):
        raise NotImplementedError()

    def delete(self, client_id, key=None):
        raise NotImplementedError()

    def by_key(self, key):
        raise NotImplementedError()

    def by_client_id(self, client_id):
        raise NotImplementedError()

if not getattr(settings, 'DACH_CONFIG').get('storage', None):
    from django.db.models import Q
    from dach.models import DachObject

    class DatabaseBackend(AbstractBackend):

        def get(self, client_id, key):
            obj = DachObject.objects.get_or_none(pk=_key(client_id, key))
            return obj.value if obj else None

        def set(self, client_id, key, value):
            DachObject.objects.update_or_create(
                pk=_key(client_id, key),
                defaults={'value': value}
            )

        def delete(self, client_id, key=None):
            if key:
                DachObject.objects.filter(pk=_key(client_id, key)).delete()
            else:
                DachObject.objects.filter(
                    pk__startswith='{}:'.format(client_id)).delete()

        def by_key(self, key):
            return {obj.id: obj.value
                for obj in DachObject.objects.filter(
                        pk__endswith=':{}'.format(key))}

        def by_client_id(self, client_id):
            return {obj.id: obj.value
                for obj in DachObject.objects.filter(
                        pk__startswith='{}:'.format(client_id))}

    __backend = DatabaseBackend()

elif 'redis' in getattr(settings, 'DACH_CONFIG')['storage']:
    import redis

    class RedisBackend(AbstractBackend):

        def __init__(self):
            conn_params = getattr(settings, 'DACH_CONFIG')['storage']['redis']
            self.client = redis.Redis(**conn_params)

        def get(self, client_id, key):
            return self.client.get(_key(client_id, key))

        def set(self, client_id, key, value):
            self.client.set(_key(client_id, key), value)

        def delete(self, client_id, key=None):
            keys = self.client.keys(_key(client_id, key or '*'))
            if keys:
                self.client.delete(*keys)

        def by_key(self, key):
            return self.client.get(_key('*', key))

        def by_client_id(self, client_id):
            return self.client.get(_key(client_id, '*'))

    __backend = RedisBackend()
