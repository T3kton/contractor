# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0001_initial'),
        ('Building', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseJob',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('state', models.CharField(choices=[('queued', 'queued'), ('waiting', 'waiting'), ('done', 'done'), ('paused', 'paused'), ('error', 'error'), ('aborted', 'aborted')], max_length=10)),
                ('status', contractor.fields.JSONField(blank=True, default=[])),
                ('message', models.CharField(blank=True, default='', max_length=1024)),
                ('script_runner', models.BinaryField()),
                ('script_name', models.CharField(editable=False, default=False, max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FoundationJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='Foreman.BaseJob', parent_link=True)),
                ('foundation', models.OneToOneField(to='Building.Foundation', editable=False)),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='StructureJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='Foreman.BaseJob', parent_link=True)),
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
