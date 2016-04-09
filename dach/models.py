from django.db import models


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
    capabilities_doc = models.FileField(
        upload_to='capabilities_doc/',
        null=False
    )


class Token(DachModel):

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
