from django.db import models
from django.conf import settings


if not getattr(settings, 'DACH_CONFIG').get('storage', None):

    __all__ = ['DachObject']

    class DachManager(models.Manager):
        def get_or_none(self, *args, **kwargs):
            try:
                return self.get(*args, **kwargs)
            except self.model.DoesNotExist:
                return None

    class DachObject(models.Model):

        objects = DachManager()

        id = models.CharField(
            primary_key=True,
            max_length=1024
        )

        value = models.TextField(
            null=False
        )
