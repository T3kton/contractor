# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Building', '0002_initial2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='structure',
            name='config_values',
            field=contractor.fields.MapField(default=dict, blank=True),
        ),
    ]
