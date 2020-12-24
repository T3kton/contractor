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
            name='Cartographer',
            fields=[
                ('identifier', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('message', models.CharField(max_length=200)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foundation', models.OneToOneField(to='Building.Foundation', null=True, on_delete=django.db.models.deletion.PROTECT, blank=True)),
            ],
            options={'default_permissions': ('delete', 'view')},
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
    ]
