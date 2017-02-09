# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0001_initial'),
        ('Utilities', '0001_initial'),
        ('BluePrint', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('locator', models.CharField(max_length=100)),
                ('id_map', contractor.fields.JSONField(blank=True)),
                ('located_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.FoundationBluePrint')),
            ],
        ),
        migrations.CreateModel(
            name='FoundationNetworkInterface',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foundation', models.ForeignKey(to='Building.Foundation')),
                ('interface', models.ForeignKey(to='Utilities.PhysicalNetworkInterface')),
            ],
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('networked_ptr', models.OneToOneField(to='Utilities.Networked', serialize=False, primary_key=True, parent_link=True, auto_created=True)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('auto_build', models.BooleanField(default=True)),
                ('build_priority', models.IntegerField(default=100)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.StructureBluePrint')),
                ('foundation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Building.Foundation')),
            ],
            bases=('Utilities.networked',),
        ),
        migrations.AddField(
            model_name='foundation',
            name='interfaces',
            field=models.ManyToManyField(through='Building.FoundationNetworkInterface', to='Utilities.PhysicalNetworkInterface'),
        ),
        migrations.AddField(
            model_name='foundation',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site'),
        ),
        migrations.AddField(
            model_name='complex',
            name='members',
            field=models.ManyToManyField(to='Building.Structure'),
        ),
        migrations.AddField(
            model_name='complex',
            name='site',
            field=models.ForeignKey(to='Site.Site'),
        ),
    ]
