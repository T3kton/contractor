# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Utilities', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aggregatednetworkinterface',
            name='paramaters',
            field=contractor.fields.MapField(default=dict),
        ),
    ]
