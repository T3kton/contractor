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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('state', models.CharField(choices=[('working', 'working'), ('waiting', 'waiting'), ('done', 'done'), ('pause', 'pause'), ('error', 'error')], max_length=10)),
                ('script_pos', contractor.fields.JSONField(default={}, editable=False)),
                ('script_ast', contractor.fields.JSONField(default={}, editable=False)),
                ('script_name', models.CharField(default=False, max_length=20, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FoundationJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(to='Foreman.BaseJob', serialize=False, parent_link=True, primary_key=True, auto_created=True)),
                ('foundation', models.OneToOneField(editable=False, to='Building.Foundation')),
            ],
            bases=('Foreman.basejob',),
        ),
        migrations.CreateModel(
            name='StructureJob',
            fields=[
                ('basejob_ptr', models.OneToOneField(to='Foreman.BaseJob', serialize=False, parent_link=True, primary_key=True, auto_created=True)),
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
