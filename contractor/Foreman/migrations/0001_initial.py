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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('state', models.CharField(choices=[('queued', 'queued'), ('waiting', 'waiting'), ('done', 'done'), ('paused', 'paused'), ('error', 'error'), ('aborted', 'aborted')], max_length=10)),
                ('status', contractor.fields.JSONField(blank=True, default=[])),
                ('message', models.CharField(blank=True, max_length=1024, default='')),
                ('script_runner', models.BinaryField()),
                ('script_name', models.CharField(editable=False, max_length=40, default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('basejob_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='Foreman.BaseJob', parent_link=True, serialize=False)),
                ('dependency', models.OneToOneField(editable=False, to='Building.Dependency')),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='FoundationJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='Foreman.BaseJob', parent_link=True, serialize=False)),
                ('foundation', models.OneToOneField(editable=False, to='Building.Foundation')),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='StructureJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='Foreman.BaseJob', parent_link=True, serialize=False)),
                ('structure', models.OneToOneField(editable=False, to='Building.Structure')),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.AddField(
            model_name='basejob',
            name='site',
            field=models.ForeignKey(to='Site.Site', editable=False),
        ),
    ]
