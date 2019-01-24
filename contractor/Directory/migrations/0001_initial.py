# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=20, choices=[('MX', 'MX'), ('SRV', 'SRV'), ('CNAME', 'CNAME'), ('TXT', 'TXT')])),
                ('name', models.CharField(max_length=255)),
                ('priority', models.IntegerField(null=True, blank=True)),
                ('weight', models.IntegerField(null=True, blank=True)),
                ('port', models.IntegerField(null=True, blank=True)),
                ('target', models.CharField(max_length=255)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('ttl', models.IntegerField(default=3600)),
                ('refresh', models.IntegerField(default=86400)),
                ('retry', models.IntegerField(default=7200)),
                ('expire', models.IntegerField(default=36000)),
                ('minimum', models.IntegerField(default=172800)),
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
