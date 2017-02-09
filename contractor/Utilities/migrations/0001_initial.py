# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0001_initial'),
        ('BluePrint', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('offset', models.IntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AddressBlock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('subnet', models.GenericIPAddressField(blank=True, null=True)),
                ('prefix', models.IntegerField()),
                ('gateway', models.GenericIPAddressField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cluster', models.ForeignKey(to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicAddress',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('offset', models.IntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('block', models.ForeignKey(to='Utilities.AddressBlock')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Networked',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('hostname', models.CharField(max_length=100)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReservedAddress',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('offset', models.IntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=50)),
                ('block', models.ForeignKey(to='Utilities.AddressBlock')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhysicalNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', parent_link=True, auto_created=True)),
                ('mac', models.CharField(primary_key=True, serialize=False, max_length=18)),
                ('physical_name', models.CharField(max_length=20)),
                ('pxe', models.ForeignKey(to='BluePrint.PXE', related_name='+')),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='VirtualNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', primary_key=True, serialize=False, parent_link=True, auto_created=True)),
                ('logical_name', models.CharField(max_length=20)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.AddField(
            model_name='address',
            name='block',
            field=models.ForeignKey(to='Utilities.AddressBlock'),
        ),
        migrations.AddField(
            model_name='address',
            name='networked',
            field=models.ForeignKey(to='Utilities.Networked'),
        ),
        migrations.CreateModel(
            name='AggragatedNetworkInterface',
            fields=[
                ('virtualnetworkinterface_ptr', models.OneToOneField(to='Utilities.VirtualNetworkInterface', primary_key=True, serialize=False, parent_link=True, auto_created=True)),
                ('paramaters', contractor.fields.MapField(default={})),
                ('master_interface', models.ForeignKey(to='Utilities.NetworkInterface', related_name='+')),
                ('slaves', models.ManyToManyField(related_name='_aggragatednetworkinterface_slaves_+', to='Utilities.NetworkInterface')),
            ],
            bases=('Utilities.virtualnetworkinterface',),
        ),
        migrations.AlterUniqueTogether(
            name='networked',
            unique_together=set([('site', 'hostname')]),
        ),
    ]
