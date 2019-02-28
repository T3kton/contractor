# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.Building.models
import contractor.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BluePrint', '0001_initial'),
        ('Utilities', '0001_initial'),
        ('Site', '0001_initial'),
        ('Building', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('networked_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.Networked', serialize=False)),
                ('config_uuid', models.CharField(unique=True, max_length=36, default=contractor.Building.models.getUUID)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('auto_build', models.BooleanField(default=True)),
                ('built_at', models.DateTimeField(blank=True, null=True, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.StructureBluePrint')),
                ('foundation', models.OneToOneField(to='Building.Foundation', on_delete=django.db.models.deletion.PROTECT)),
            ],
            bases=('Utilities.networked',),
        ),
        migrations.AddField(
            model_name='foundation',
            name='blueprint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.FoundationBluePrint'),
        ),
        migrations.AddField(
            model_name='foundation',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site'),
        ),
        migrations.AddField(
            model_name='dependency',
            name='dependency',
            field=models.ForeignKey(to='Building.Dependency', blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='dependency',
            name='foundation',
            field=models.OneToOneField(to='Building.Foundation', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dependency',
            name='script_structure',
            field=models.ForeignKey(to='Building.Structure', blank=True, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='dependency',
            name='structure',
            field=models.ForeignKey(to='Building.Structure', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='complexstructure',
            name='complex',
            field=models.ForeignKey(to='Building.Complex'),
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
    ]
