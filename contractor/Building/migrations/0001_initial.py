# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('built_percentage', models.IntegerField(default=90)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={'default_permissions': (), 'permissions': (('can_create_foundation', 'Can Create Foundations'),)},
        ),
        migrations.CreateModel(
            name='ComplexStructure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dependency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('link', models.CharField(max_length=4, choices=[('soft', 'soft'), ('hard', 'hard')])),
                ('create_script_name', models.CharField(null=True, max_length=40, blank=True)),
                ('destroy_script_name', models.CharField(null=True, max_length=40, blank=True)),
                ('built_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={'permissions': (('can_create_dependency_job', 'Can Create Dependency Jobs'),)},
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('locator', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('id_map', contractor.fields.JSONField(null=True, blank=True)),
                ('located_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('built_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={'default_permissions': (), 'permissions': (('can_create_foundation_job', 'Can Create Foundation Jobs'),)},
        ),
    ]
