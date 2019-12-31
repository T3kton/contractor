# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Building', '0002_initial2'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoundationBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=2048)),
                ('proxy', models.CharField(null=True, max_length=512, blank=True)),
                ('type', models.CharField(max_length=4, choices=[('post', 'POST'), ('call', 'call (CINP)')])),
                ('one_shot', models.BooleanField(default=True)),
                ('extra_data', contractor.fields.MapField(default=contractor.fields.defaultdict)),
                ('expires', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foundation', models.ForeignKey(related_name='+', to='Building.Foundation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FoundationPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('foundation', models.ForeignKey(related_name='+', to='Building.Foundation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StructureBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=2048)),
                ('proxy', models.CharField(null=True, max_length=512, blank=True)),
                ('type', models.CharField(max_length=4, choices=[('post', 'POST'), ('call', 'call (CINP)')])),
                ('one_shot', models.BooleanField(default=True)),
                ('extra_data', contractor.fields.MapField(default=contractor.fields.defaultdict)),
                ('expires', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('structure', models.ForeignKey(related_name='+', to='Building.Structure')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StructurePost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('structure', models.ForeignKey(related_name='+', to='Building.Structure')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
