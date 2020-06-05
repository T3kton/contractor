# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.Building.models
import django.db.models.deletion
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Utilities', '0001_initial'),
        ('BluePrint', '0001_initial'),
        ('Building', '0001_initial'),
        ('Site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('networked_ptr', models.OneToOneField(to='Utilities.Networked', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('config_uuid', models.CharField(default=contractor.Building.models.getUUID, max_length=36, unique=True)),
                ('config_values', contractor.fields.MapField(null=True, default=contractor.fields.defaultdict, blank=True)),
                ('built_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.StructureBluePrint')),
                ('foundation', models.OneToOneField(related_name='+', to='Building.Foundation', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={'permissions': (('can_create_structure_job', 'Can Create Structure Jobs'), ('can_config_structure', 'Can Update Structure Config Values'))},
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
            field=models.ForeignKey(null=True, blank=True, to='Building.Dependency', related_name='+'),
        ),
        migrations.AddField(
            model_name='dependency',
            name='foundation',
            field=models.OneToOneField(related_name='+', null=True, to='Building.Foundation', blank=True),
        ),
        migrations.AddField(
            model_name='dependency',
            name='script_structure',
            field=models.ForeignKey(null=True, blank=True, to='Building.Structure', related_name='+'),
        ),
        migrations.AddField(
            model_name='dependency',
            name='structure',
            field=models.ForeignKey(related_name='+', null=True, blank=True, to='Building.Structure'),
        ),
        migrations.AddField(
            model_name='complexstructure',
            name='complex',
            field=models.ForeignKey(to='Building.Complex'),
        ),
        migrations.AddField(
            model_name='complexstructure',
            name='structure',
            field=models.OneToOneField(to='Building.Structure'),
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
    ]
