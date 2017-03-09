# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields

def load_structure_blueprints( app, schema_editor ):
  StructureBluePrint = app.get_model( 'BluePrint', 'StructureBluePrint' )
  Script = app.get_model( 'BluePrint', 'Script' )
  BluePrintScript = app.get_model( 'BluePrint', 'BluePrintScript' )

  sbpl = StructureBluePrint( name='generic-linux', description='Generic Linux' )
  sbpl.config_values = { 'distro': 'generic' }
  sbpl.full_clean()
  sbpl.save()

  sbpu = StructureBluePrint( name='generic-ubuntu', description='Generic Ubuntu' )
  sbpu.config_values = { 'distro': 'ubuntu' }
  sbpu.parent = sbpl
  sbpu.full_clean()
  sbpu.save()

  sbpx = StructureBluePrint( name='generic-xenial', description='Generic Ubuntu Xenial (16.04 LTS)' )
  sbpx.config_values = { 'distro_version': 'xenial' }
  sbpx.parent = sbpu
  sbpx.full_clean()
  sbpx.save()

  s = Script( name='create-linux', description='Install Linux' )
  s.script = """# pxe boot and install
foundation.power_on()
"""
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=sbpl, script=s, name='create' ).save()

  s = Script( name='destroy-linux', description='Uninstall Linux' )
  s.script = """# nothing to do, foundation cleanup should wipe/destroy the disks
foundation.power_off()
"""
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=sbpl, script=s, name='destroy' ).save()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrint',
            fields=[
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BluePrintScript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PXE',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('script', models.TextField()),
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
                ('blueprint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, to='BluePrint.BluePrint', serialize=False)),
                ('foundation_type_list', contractor.fields.StringListField(max_length=200, default=[])),
                ('template', contractor.fields.JSONField(default={}, blank=True)),
                ('physical_interface_names', contractor.fields.StringListField(max_length=200, default=[])),
                ('parent', models.ForeignKey(blank=True, null=True, to='BluePrint.FoundationBluePrint')),
            ],
            bases=('BluePrint.blueprint',),
        ),
        migrations.CreateModel(
            name='StructureBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, to='BluePrint.BluePrint', serialize=False)),
                ('foundation_blueprint_list', models.ManyToManyField(to='BluePrint.FoundationBluePrint')),
                ('parent', models.ForeignKey(blank=True, null=True, to='BluePrint.StructureBluePrint')),
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
        migrations.RunPython( load_structure_blueprints ),
    ]
