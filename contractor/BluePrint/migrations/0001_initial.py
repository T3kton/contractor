# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrint',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=40, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BluePrintScript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PXE',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=50, serialize=False)),
                ('boot_script', models.TextField()),
                ('template', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=40, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('script', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FoundationBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(primary_key=True, parent_link=True, auto_created=True, to='BluePrint.BluePrint', serialize=False)),
                ('foundation_type_list', contractor.fields.StringListField(max_length=200, default=[])),
                ('template', contractor.fields.JSONField(blank=True, default={})),
                ('physical_interface_names', contractor.fields.StringListField(blank=True, max_length=200, default=[])),
                ('parent_list', models.ManyToManyField(to='BluePrint.FoundationBluePrint', blank=True)),
            ],
            bases=('BluePrint.blueprint',),
        ),
        migrations.CreateModel(
            name='StructureBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(primary_key=True, parent_link=True, auto_created=True, to='BluePrint.BluePrint', serialize=False)),
                ('foundation_blueprint_list', models.ManyToManyField(to='BluePrint.FoundationBluePrint')),
                ('parent_list', models.ManyToManyField(to='BluePrint.StructureBluePrint', blank=True)),
            ],
            bases=('BluePrint.blueprint',),
        ),
        migrations.AddField(
            model_name='blueprintscript',
            name='blueprint',
            field=models.ForeignKey(to='BluePrint.BluePrint'),
        ),
        migrations.AddField(
            model_name='blueprintscript',
            name='script',
            field=models.ForeignKey(to='BluePrint.Script'),
        ),
        migrations.AddField(
            model_name='blueprint',
            name='scripts',
            field=models.ManyToManyField(to='BluePrint.Script', through='BluePrint.BluePrintScript'),
        ),
        migrations.AlterUniqueTogether(
            name='blueprintscript',
            unique_together=set([('blueprint', 'name')]),
        ),
    ]
