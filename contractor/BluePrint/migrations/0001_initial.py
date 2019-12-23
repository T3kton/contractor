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
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('config_values', contractor.fields.MapField(null=True, default=contractor.fields.defaultdict, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BluePrintScript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PXE',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('boot_script', models.TextField()),
                ('template', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('script', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FoundationBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(to='BluePrint.BluePrint', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('foundation_type_list', contractor.fields.StringListField(default=list, max_length=200)),
                ('template', contractor.fields.MapField(default=contractor.fields.defaultdict, null=True, blank=True)),
                ('physical_interface_names', contractor.fields.StringListField(blank=True, default=list, max_length=200)),
                ('parent_list', models.ManyToManyField(blank=True, to='BluePrint.FoundationBluePrint')),
            ],
            bases=('BluePrint.blueprint',),
        ),
        migrations.CreateModel(
            name='StructureBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(to='BluePrint.BluePrint', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('foundation_blueprint_list', models.ManyToManyField(to='BluePrint.FoundationBluePrint')),
                ('parent_list', models.ManyToManyField(blank=True, to='BluePrint.StructureBluePrint')),
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
            field=models.ManyToManyField(through='BluePrint.BluePrintScript', to='BluePrint.Script'),
        ),
        migrations.AlterUniqueTogether(
            name='blueprintscript',
            unique_together=set([('blueprint', 'name')]),
        ),
    ]
