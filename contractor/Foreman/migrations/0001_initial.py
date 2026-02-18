# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0001_initial'),
        ('Building', '0002_initial2'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseJob',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('state', models.CharField(max_length=10, choices=[('queued', 'queued'), ('waiting', 'waiting'), ('done', 'done'), ('paused', 'paused'), ('error', 'error'), ('aborted', 'aborted')])),
                ('status', contractor.fields.JSONField(default=[], blank=True)),
                ('message', models.CharField(default='', max_length=1024, blank=True)),
                ('script_runner', models.BinaryField()),
                ('script_name', models.CharField(default=False, max_length=40, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={'default_permissions': (), 'permissions': (('can_base_job', 'Can Work With Base Jobs'), ('can_job_signal', 'Can call the Job Signalling Actions'))},
        ),
        migrations.CreateModel(
            name='JobLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('job_id', models.IntegerField()),
                ('target_class', models.CharField(max_length=50)),
                ('target_id', models.CharField(max_length=100)),
                ('target_description', models.CharField(max_length=120)),
                ('script_name', models.CharField(max_length=50)),
                ('creator', models.CharField(max_length=150)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('canceled_by', models.CharField(max_length=150, null=True, blank=True)),
                ('canceled_at', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(to='Site.Site',on_delete=models.CASCADE)),
            ],
            options={'default_permissions': ('view',)},
        ),
        migrations.CreateModel(
            name='DependencyJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(primary_key=True, serialize=False, parent_link=True, auto_created=True, to='Foreman.BaseJob',on_delete=models.CASCADE)),
                ('dependency', models.OneToOneField(editable=False, to='Building.Dependency',on_delete=models.CASCADE)),
            ],
            bases=('Foreman.basejob',),
            options={'default_permissions': ('view',), 'permissions': (('can_dependency_job', 'Can Work With Dependency Jobs'),)},
        ),
        migrations.CreateModel(
            name='FoundationJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(primary_key=True, serialize=False, parent_link=True, auto_created=True, to='Foreman.BaseJob',on_delete=models.CASCADE)),
                ('foundation', models.OneToOneField(editable=False, to='Building.Foundation',on_delete=models.CASCADE)),
            ],
            bases=('Foreman.basejob',),
            options={'default_permissions': ('view',), 'permissions': (('can_foundation_job', 'Can Work With Foundation Jobs'),)},
        ),
        migrations.CreateModel(
            name='StructureJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(primary_key=True, serialize=False, parent_link=True, auto_created=True, to='Foreman.BaseJob',on_delete=models.CASCADE)),
                ('structure', models.OneToOneField(editable=False, to='Building.Structure',on_delete=models.CASCADE)),
            ],
            bases=('Foreman.basejob',),
            options={'default_permissions': ('view',), 'permissions': (('can_structure_job', 'Can Work With Structure Jobs'),)},
        ),
        migrations.AddField(
            model_name='basejob',
            name='site',
            field=models.ForeignKey(editable=False, to='Site.Site',on_delete=models.CASCADE),
        ),
    ]
