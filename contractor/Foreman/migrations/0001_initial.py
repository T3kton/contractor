# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Building', '0001_initial'),
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
            name='DependancyJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(parent_link=True, to='Foreman.BaseJob', auto_created=True, primary_key=True, serialize=False)),
                ('dependancy', models.OneToOneField(to='Building.Dependancy', editable=False)),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='FoundationJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(parent_link=True, to='Foreman.BaseJob', auto_created=True, primary_key=True, serialize=False)),
                ('foundation', models.OneToOneField(to='Building.Foundation', editable=False)),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='StructureJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(parent_link=True, to='Foreman.BaseJob', auto_created=True, primary_key=True, serialize=False)),
                ('structure', models.OneToOneField(to='Building.Structure', editable=False)),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.AddField(
            model_name='basejob',
            name='site',
            field=models.ForeignKey(editable=False, to='Site.Site'),
        ),
    ]
