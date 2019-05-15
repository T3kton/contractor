# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Building', '0002_initial2'),
        ('Site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('state', models.CharField(max_length=10, choices=[('queued', 'queued'), ('waiting', 'waiting'), ('done', 'done'), ('paused', 'paused'), ('error', 'error'), ('aborted', 'aborted')])),
                ('status', contractor.fields.JSONField(blank=True, default=[])),
                ('message', models.CharField(blank=True, default='', max_length=1024)),
                ('script_runner', models.BinaryField()),
                ('script_name', models.CharField(default=False, max_length=40, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('job_id', models.IntegerField()),
                ('target_class', models.CharField(max_length=50)),
                ('target_description', models.CharField(max_length=120)),
                ('script_name', models.CharField(max_length=50)),
                ('start_finish', models.BooleanField()),
                ('at', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='DependencyJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(to='Foreman.BaseJob', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('dependency', models.OneToOneField(to='Building.Dependency', editable=False)),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='FoundationJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(to='Foreman.BaseJob', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('foundation', models.OneToOneField(to='Building.Foundation', editable=False)),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='StructureJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(to='Foreman.BaseJob', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('structure', models.OneToOneField(to='Building.Structure', editable=False)),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.AddField(
            model_name='basejob',
            name='site',
            field=models.ForeignKey(to='Site.Site', editable=False),
        ),
    ]
