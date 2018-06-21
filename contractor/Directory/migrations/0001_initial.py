# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('type', models.CharField(max_length=20, choices=[('MX', 'MX'), ('SRV', 'SRV'), ('CNAME', 'CNAME'), ('TXT', 'TXT')])),
                ('name', models.CharField(max_length=255)),
                ('priority', models.IntegerField(blank=True, null=True)),
                ('weight', models.IntegerField(blank=True, null=True)),
                ('port', models.IntegerField(blank=True, null=True)),
                ('target', models.CharField(max_length=255)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('ttl', models.IntegerField(default=3600)),
                ('refresh', models.IntegerField(default=86400)),
                ('retry', models.IntegerField(default=7200)),
                ('expire', models.IntegerField(default=36000)),
                ('minimum', models.IntegerField(default=172800)),
                ('email', models.CharField(max_length=150)),
                ('ns_list', contractor.fields.StringListField(max_length=400, default=[], blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(null=True, blank=True, to='Directory.Zone')),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='zone',
            field=models.ForeignKey(to='Directory.Zone'),
        ),
        migrations.AlterUniqueTogether(
            name='zone',
            unique_together=set([('name', 'parent')]),
        ),
    ]
