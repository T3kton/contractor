# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields

def load_blueprints( app, schema_editor ):
  FoundationBluePrint = app.get_model( 'BluePrint', 'FoundationBluePrint' )
  StructureBluePrint = app.get_model( 'BluePrint', 'StructureBluePrint' )
  Script = app.get_model( 'BluePrint', 'Script' )
  BluePrintScript = app.get_model( 'BluePrint', 'BluePrintScript' )

  fbp = FoundationBluePrint( name='generic-virtualbox', description='Generic VirtualBox VM' )
  fbp.config_values = {}
  fbp.template = {}
  fbp.physical_interface_names = [ 'eth0' ]
  fbp.save()

  sbpl = StructureBluePrint( name='generic-linux', description='Generic Linux' )
  sbpl.save()
  sbpl.foundation_blueprint_list = [ fbp ]
  sbpl.save()

  sbpu = StructureBluePrint( name='generic-ubuntu', description='Generic Ubuntu' )
  sbpu.parent = sbpl
  sbpu.save()

  sbpx = StructureBluePrint( name='generic-xenial', description='Generic Ubuntu Xenial (16.04 LTS)' )
  sbpx.parent = sbpu
  sbpx.save()

  s = Script( name='create-virtualbox', description='Create VirtualBox VM' )
  s.script = '# create VM'
  s.save()
  BluePrintScript( blueprint=fbp, script=s, name='create' ).save()

  s = Script( name='destroy-virtualbox', description='Destroy VirtualBox VM' )
  s.script = '# remove vm'
  s.save()
  BluePrintScript( blueprint=fbp, script=s, name='destroy' ).save()

  s = Script( name='create-linux', description='Install Linux' )
  s.script = '# pxe boot and install'
  s.save()
  BluePrintScript( blueprint=sbpl, script=s, name='create' ).save()

  s = Script( name='destroy-linux', description='Uninstall Linux' )
  s.script = '# nothing to do, foundation cleanup should wipe/destroy the disks'
  s.save()
  BluePrintScript( blueprint=sbpl, script=s, name='destroy' ).save()

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrint',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=20)),
                ('description', models.CharField(max_length=200)),
                ('config_values', contractor.fields.MapField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BluePrintScript',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PXE',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=50)),
                ('script', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=20)),
                ('description', models.CharField(max_length=200)),
                ('script', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FoundationBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(to='BluePrint.BluePrint', serialize=False, primary_key=True, auto_created=True, parent_link=True)),
                ('template', contractor.fields.JSONField()),
                ('physical_interface_names', contractor.fields.StringListField(default=[], max_length=200)),
            ],
            bases=('BluePrint.blueprint',),
        ),
        migrations.CreateModel(
            name='StructureBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(to='BluePrint.BluePrint', serialize=False, primary_key=True, auto_created=True, parent_link=True)),
                ('foundation_blueprint_list', models.ManyToManyField(to='BluePrint.FoundationBluePrint')),
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
            name='parent',
            field=models.ForeignKey(null=True, blank=True, to='BluePrint.BluePrint'),
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
        migrations.RunPython( load_blueprints ),
    ]
