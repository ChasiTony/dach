from django.db import models
from django.conf import settings


if not getattr(settings, 'DACH_STORAGE', None):

    __all__ = ['Tenant', 'Token']

    class DachManager(models.Manager):
        def get_or_none(self, *args, **kwargs):
            try:
                return self.get(*args, **kwargs)
            except self.model.DoesNotExist:
                return None

    class DachModel(models.Model):
        class Meta:
            abstract = True

        objects = DachManager()

        oauth_id = models.CharField(
            primary_key=True,
            max_length=255
        )
        group_id = models.PositiveIntegerField(
            null=False
        )
        group_name = models.CharField(
            max_length=255,
            null=False,
            blank=False
        )

        def to_dict(self):
            d = dict()
            for field in self._meta.fields:
                d[field.name] = getattr(self, field.name)
            return d

    class Tenant(DachModel):

        oauth_secret = models.CharField(
            max_length=255,
            null=False,
            blank=False
        )
        room_id = models.PositiveIntegerField()
        capabilities_url = models.URLField(
            null=False
        )
        oauth_token_url = models.URLField(
            null=False
        )
        api_url = models.URLField(
            null=False
        )

    class Token(DachModel):
        class Meta:
            index_together = [
                ('oauth_id', 'scope')
            ]

        access_token = models.CharField(
            max_length=255,
            null=False,
            blank=False
        )
        expires_in = models.PositiveIntegerField(
            null=False
        )

        scope = models.CharField(
            max_length=255,
            null=False,
            blank=False
        )
        token_type = models.CharField(
            max_length=255,
            null=False,
            blank=False
        )
        created = models.DateTimeField(
            null=False,
            auto_now_add=True
        )


