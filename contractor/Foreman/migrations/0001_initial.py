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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('state', models.CharField(choices=[('queued', 'queued'), ('waiting', 'waiting'), ('done', 'done'), ('paused', 'paused'), ('error', 'error'), ('aborted', 'aborted')], max_length=10)),
                ('status', contractor.fields.JSONField(default=[], blank=True)),
                ('message', models.CharField(default='', blank=True, max_length=1024)),
                ('script_runner', models.BinaryField()),
                ('script_name', models.CharField(default=False, editable=False, max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobLog',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('job_id', models.IntegerField()),
                ('creator', models.CharField(max_length=150)),
                ('target_class', models.CharField(max_length=50)),
                ('target_description', models.CharField(max_length=120)),
                ('script_name', models.CharField(max_length=50)),
                ('start_finish', models.BooleanField()),
                ('at', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='DependencyJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='Foreman.BaseJob', serialize=False, primary_key=True)),
                ('dependency', models.OneToOneField(editable=False, to='Building.Dependency')),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='FoundationJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='Foreman.BaseJob', serialize=False, primary_key=True)),
                ('foundation', models.OneToOneField(editable=False, to='Building.Foundation')),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='StructureJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='Foreman.BaseJob', serialize=False, primary_key=True)),
                ('structure', models.OneToOneField(editable=False, to='Building.Structure')),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.AddField(
            model_name='basejob',
            name='site',
            field=models.ForeignKey(editable=False, to='Site.Site'),
        ),
    ]
