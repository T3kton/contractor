# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('config_values', contractor.fields.MapField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, to='Site.Site')),
            ],
        ),
    ]
