# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields
import django.db.models.deletion
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
        ('Utilities', '0001_initial'),
        ('Site', '0001_initial'),
        ('BluePrint', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('name', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('built_percentage', models.IntegerField(default=90)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ComplexStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.ForeignKey(to='Building.Complex')),
            ],
        ),
        migrations.CreateModel(
            name='Dependancy',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('link', models.CharField(max_length=4, choices=[('soft', 'soft'), ('hard', 'hard')])),
                ('create_script_name', models.CharField(null=True, max_length=40, blank=True)),
                ('destroy_script_name', models.CharField(null=True, max_length=40, blank=True)),
                ('built_at', models.DateTimeField(null=True, blank=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('dependancy', models.ForeignKey(null=True, related_name='+', to='Building.Dependancy', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('locator', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('id_map', contractor.fields.JSONField(blank=True)),
                ('located_at', models.DateTimeField(null=True, blank=True, editable=False)),
                ('built_at', models.DateTimeField(null=True, blank=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='BluePrint.FoundationBluePrint', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='FoundationNetworkInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('physical_location', models.CharField(max_length=100)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foundation', models.ForeignKey(to='Building.Foundation')),
                ('interface', models.ForeignKey(to='Utilities.RealNetworkInterface')),
            ],
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('networked_ptr', models.OneToOneField(to='Utilities.Networked', auto_created=True, parent_link=True, serialize=False, primary_key=True)),
                ('config_uuid', models.CharField(max_length=36, unique=True, default=contractor.Building.models.getUUID)),
                ('config_values', contractor.fields.MapField(default={}, blank=True)),
                ('auto_build', models.BooleanField(default=True)),
                ('built_at', models.DateTimeField(null=True, blank=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='BluePrint.StructureBluePrint', on_delete=django.db.models.deletion.PROTECT)),
                ('foundation', models.OneToOneField(to='Building.Foundation', on_delete=django.db.models.deletion.PROTECT)),
            ],
            bases=('Utilities.networked',),
        ),
        migrations.AddField(
            model_name='foundation',
            name='interfaces',
            field=models.ManyToManyField(to='Utilities.RealNetworkInterface', through='Building.FoundationNetworkInterface'),
        ),
        migrations.AddField(
            model_name='foundation',
            name='site',
            field=models.ForeignKey(to='Site.Site', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='dependancy',
            name='foundation',
            field=models.OneToOneField(null=True, to='Building.Foundation', blank=True),
        ),
        migrations.AddField(
            model_name='dependancy',
            name='script_structure',
            field=models.ForeignKey(null=True, related_name='+', to='Building.Structure', blank=True),
        ),
        migrations.AddField(
            model_name='dependancy',
            name='structure',
            field=models.ForeignKey(null=True, to='Building.Structure', blank=True),
        ),
        migrations.AddField(
            model_name='complexstructure',
            name='structure',
            field=models.ForeignKey(to='Building.Structure'),
        ),
        migrations.AddField(
            model_name='complex',
            name='members',
            field=models.ManyToManyField(to='Building.Structure', through='Building.ComplexStructure'),
        ),
        migrations.AddField(
            model_name='complex',
            name='site',
            field=models.ForeignKey(to='Site.Site'),
        ),
        migrations.RunPython( load_foundation_blueprints ),
    ]
