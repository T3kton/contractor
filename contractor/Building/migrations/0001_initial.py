# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.Building.models
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.ForeignKey(to='Building.Complex')),
            ],
        ),
        migrations.CreateModel(
            name='Dependancy',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('link', models.CharField(choices=[('soft', 'soft'), ('hard', 'hard')], max_length=4)),
                ('create_script_name', models.CharField(null=True, max_length=40, blank=True)),
                ('destroy_script_name', models.CharField(null=True, max_length=40, blank=True)),
                ('built_at', models.DateTimeField(null=True, blank=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('dependancy', models.ForeignKey(null=True, related_name='+', blank=True, to='Building.Dependancy')),
            ],
        ),
        migrations.CreateModel(
            name='Foundation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('locator', models.CharField(max_length=100, unique=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
                ('networked_ptr', models.OneToOneField(auto_created=True, serialize=False, to='Utilities.Networked', parent_link=True, primary_key=True)),
                ('config_uuid', models.CharField(max_length=36, default=contractor.Building.models.getUUID, unique=True)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
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
            field=models.ManyToManyField(through='Building.FoundationNetworkInterface', to='Utilities.RealNetworkInterface'),
        ),
        migrations.AddField(
            model_name='foundation',
            name='site',
            field=models.ForeignKey(to='Site.Site', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='dependancy',
            name='foundation',
            field=models.OneToOneField(null=True, blank=True, to='Building.Foundation'),
        ),
        migrations.AddField(
            model_name='dependancy',
            name='script_structure',
            field=models.ForeignKey(null=True, related_name='+', blank=True, to='Building.Structure'),
        ),
        migrations.AddField(
            model_name='dependancy',
            name='structure',
            field=models.ForeignKey(null=True, blank=True, to='Building.Structure'),
        ),
        migrations.AddField(
            model_name='complexstructure',
            name='structure',
            field=models.ForeignKey(to='Building.Structure'),
        ),
        migrations.AddField(
            model_name='complex',
            name='members',
            field=models.ManyToManyField(through='Building.ComplexStructure', to='Building.Structure'),
        ),
        migrations.AddField(
            model_name='complex',
            name='site',
            field=models.ForeignKey(to='Site.Site'),
        ),
        migrations.RunPython( load_foundation_blueprints ),
    ]
