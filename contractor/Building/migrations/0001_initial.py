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
                ('name', models.CharField(serialize=False, max_length=40, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('built_percentage', models.IntegerField(default=90)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ComplexStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dependancy',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('link', models.CharField(choices=[('soft', 'soft'), ('hard', 'hard')], max_length=4)),
                ('create_script_name', models.CharField(blank=True, null=True, max_length=40)),
                ('destroy_script_name', models.CharField(blank=True, null=True, max_length=40)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('locator', models.CharField(serialize=False, max_length=100, primary_key=True)),
                ('id_map', contractor.fields.JSONField(blank=True)),
                ('located_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
