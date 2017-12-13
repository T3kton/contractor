# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Building', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoundationBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('url', models.CharField(max_length=2048)),
                ('proxy', models.CharField(blank=True, max_length=512, null=True)),
                ('type', models.CharField(choices=[('post', 'POST'), ('call', 'call (CINP)')], max_length=4)),
                ('one_shot', models.BooleanField(default=True)),
                ('extra_data', contractor.fields.MapField(default={})),
                ('expires', models.DateTimeField(blank=True, null=True)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('url', models.CharField(max_length=2048)),
                ('proxy', models.CharField(blank=True, max_length=512, null=True)),
                ('type', models.CharField(choices=[('post', 'POST'), ('call', 'call (CINP)')], max_length=4)),
                ('one_shot', models.BooleanField(default=True)),
                ('extra_data', contractor.fields.MapField(default={})),
                ('expires', models.DateTimeField(blank=True, null=True)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
