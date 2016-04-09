# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('oauth_id', models.CharField(primary_key=True, max_length=255, serialize=False)),
                ('group_id', models.PositiveIntegerField()),
                ('group_name', models.CharField(max_length=255)),
                ('oauth_secret', models.CharField(max_length=255)),
                ('room_id', models.PositiveIntegerField()),
                ('capabilities_url', models.URLField()),
                ('capabilities_doc', models.FileField(upload_to='capabilities_doc/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('oauth_id', models.CharField(primary_key=True, max_length=255, serialize=False)),
                ('group_id', models.PositiveIntegerField()),
                ('group_name', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('expires_in', models.PositiveIntegerField()),
                ('scope', models.CharField(max_length=255)),
                ('token_type', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
