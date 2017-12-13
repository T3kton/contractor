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
        ('Utilities', '0001_initial'),
        ('BluePrint', '0001_initial'),
        ('Site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=40, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('built_percentage', models.IntegerField(default=90)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ComplexStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.ForeignKey(to='Building.Complex')),
            ],
        ),
        migrations.CreateModel(
            name='Dependancy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('link', models.CharField(choices=[('soft', 'soft'), ('hard', 'hard')], max_length=4)),
                ('create_script_name', models.CharField(blank=True, max_length=40, null=True)),
                ('destroy_script_name', models.CharField(blank=True, max_length=40, null=True)),
                ('built_at', models.DateTimeField(editable=False, blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('locator', models.CharField(max_length=100, unique=True)),
                ('id_map', contractor.fields.JSONField(blank=True)),
                ('located_at', models.DateTimeField(editable=False, blank=True, null=True)),
                ('built_at', models.DateTimeField(editable=False, blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.FoundationBluePrint')),
            ],
        ),
        migrations.CreateModel(
            name='FoundationNetworkInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('networked_ptr', models.OneToOneField(parent_link=True, to='Utilities.Networked', auto_created=True, primary_key=True, serialize=False)),
                ('config_uuid', models.CharField(max_length=36, default=contractor.Building.models.getUUID, unique=True)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('auto_build', models.BooleanField(default=True)),
                ('built_at', models.DateTimeField(editable=False, blank=True, null=True)),
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
            field=models.ManyToManyField(to='Utilities.RealNetworkInterface', through='Building.FoundationNetworkInterface'),
        ),
        migrations.AddField(
            model_name='foundation',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site'),
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
