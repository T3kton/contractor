# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Directory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('config_values', contractor.fields.MapField(null=True, default=contractor.fields.defaultdict, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(null=True, blank=True, to='Site.Site', on_delete=models.CASCADE)),
                ('zone', models.ForeignKey(null=True, blank=True, to='Directory.Zone', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
    ]
