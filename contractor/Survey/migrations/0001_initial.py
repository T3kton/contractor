# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Building', '0002_initial2'),
    ]

    operations = [
        migrations.CreateModel(
            name='Locator',
            fields=[
                ('identifier', models.CharField(primary_key=True, max_length=100, serialize=False)),
                ('message', models.CharField(max_length=200)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foundation', models.OneToOneField(to='Building.Foundation', on_delete=django.db.models.deletion.PROTECT, null=True, related_name='+', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plot',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=40, serialize=False)),
                ('corners', models.CharField(max_length=200)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(to='Survey.Plot', null=True, on_delete=django.db.models.deletion.PROTECT, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=40, serialize=False)),
                ('item_map', contractor.fields.MapField(default=contractor.fields.defaultdict)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
