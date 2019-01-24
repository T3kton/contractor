# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Directory', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zone',
            name='id',
        ),
        migrations.AlterField(
            model_name='zone',
            name='name',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
