# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.Building.models
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
        ('Site', '0001_initial'),
        ('BluePrint', '0001_initial'),
        ('Utilities', '0001_initial'),
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
                ('create_script_name', models.CharField(blank=True, max_length=40, null=True)),
                ('destroy_script_name', models.CharField(blank=True, max_length=40, null=True)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('locator', models.CharField(unique=True, max_length=100)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('id_map', contractor.fields.JSONField(blank=True)),
                ('located_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
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
                ('networked_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.Networked', serialize=False)),
                ('config_uuid', models.CharField(unique=True, max_length=36, default=contractor.Building.models.getUUID)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('auto_build', models.BooleanField(default=True)),
                ('build_priority', models.IntegerField(default=100)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
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
            field=models.ForeignKey(to='Building.Foundation'),
        ),
        migrations.AddField(
            model_name='dependancy',
            name='structure',
            field=models.ForeignKey(to='Building.Structure'),
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
        migrations.AlterUniqueTogether(
            name='dependancy',
            unique_together=set([('structure', 'foundation')]),
        ),
        migrations.RunPython( load_foundation_blueprints ),
    ]
