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
            field=contractor.fields.MapField(blank=True, default=contractor.fields.defaultdict, null=True),
        ),
        migrations.AlterField(
            model_name='foundation',
            name='id_map',
            field=contractor.fields.JSONField(null=True, blank=True),
        ),
    ]
