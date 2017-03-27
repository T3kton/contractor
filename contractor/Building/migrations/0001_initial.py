# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields
import django.db.models.deletion
import contractor.fields
import contractor.Building.models


def load_foundation_blueprints( app, schema_editor ):
  FoundationBluePrint = app.get_model( 'BluePrint', 'FoundationBluePrint' )
  Script = app.get_model( 'BluePrint', 'Script' )
  BluePrintScript = app.get_model( 'BluePrint', 'BluePrintScript' )

  fbp = FoundationBluePrint( name='unknown', description='Unknown Foundation' )
  fbp.config_values = {}
  fbp.template = {}
  fbp.foundation_type_list = [ 'Unknown' ]
  fbp.physical_interface_names = [ 'eth0', 'eth1', 'eth2', 'eth3' ]
  fbp.full_clean()
  fbp.save()

  s = Script( name='create-unknown', description='Create Unknown' )
  s.script = """# Create Unknown(Base) Foundation
error( 'can not create/commission unknown/base foundation' )
  """
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=fbp, script=s, name='create' ).save()

  s = Script( name='destroy-unknown', description='Create Unknown' )
  s.script = """# Destroy Unknown(Base) Foundation
error( 'can not destroy/decommission unknown/base foundation' )
  """
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=fbp, script=s, name='destroy' ).save()


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
                ('name', models.CharField(serialize=False, primary_key=True, max_length=40)),
                ('description', models.CharField(max_length=200)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('locator', models.CharField(unique=True, max_length=100)),
                ('config_values', contractor.fields.MapField(default={}, blank=True)),
                ('id_map', contractor.fields.JSONField(blank=True)),
                ('located_at', models.DateTimeField(editable=False, null=True, blank=True)),
                ('built_at', models.DateTimeField(editable=False, null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.FoundationBluePrint')),
            ],
        ),
        migrations.CreateModel(
            name='FoundationNetworkInterface',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foundation', models.ForeignKey(to='Building.Foundation')),
                ('interface', models.ForeignKey(to='Utilities.RealNetworkInterface')),
            ],
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('networked_ptr', models.OneToOneField(auto_created=True, to='Utilities.Networked', serialize=False, parent_link=True, primary_key=True)),
                ('config_uuid', models.CharField(default=contractor.Building.models.getUUID, unique=True, max_length=36)),
                ('config_values', contractor.fields.MapField(default={}, blank=True)),
                ('auto_build', models.BooleanField(default=True)),
                ('build_priority', models.IntegerField(default=100)),
                ('built_at', models.DateTimeField(editable=False, null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.StructureBluePrint')),
                ('foundation', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='Building.Foundation')),
            ],
            bases=('Utilities.networked',),
        ),
        migrations.AddField(
            model_name='foundation',
            name='interfaces',
            field=models.ManyToManyField(through='Building.FoundationNetworkInterface', to='Utilities.RealNetworkInterface'),
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
        migrations.RunPython( load_foundation_blueprints ),
    ]
