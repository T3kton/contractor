# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('BluePrint', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blueprint',
            name='config_values',
            field=contractor.fields.MapField(blank=True, default=contractor.fields.defaultdict, null=True),
        ),
        migrations.AlterField(
            model_name='foundationblueprint',
            name='foundation_type_list',
            field=contractor.fields.StringListField(default=list, max_length=200),
        ),
        migrations.AlterField(
            model_name='foundationblueprint',
            name='physical_interface_names',
            field=contractor.fields.StringListField(default=list, max_length=200, blank=True),
        ),
    ]
