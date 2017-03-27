# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('BluePrint', '0001_initial'),
        ('Site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBlock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('subnet', contractor.fields.IpAddressField()),
                ('prefix', models.IntegerField()),
                ('gateway', contractor.fields.IpAddressField(blank=True, null=True)),
                ('_max_address', contractor.fields.IpAddressField(editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cluster', models.ForeignKey(to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='BaseAddress',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('offset', models.IntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Networked',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('hostname', models.CharField(max_length=100)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AbstractNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
                ('logical_name', models.CharField(max_length=20)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
                ('is_primary', models.BooleanField(default=False)),
                ('is_provisioning', models.BooleanField(default=False)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='DynamicAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='RealNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', parent_link=True, auto_created=True)),
                ('mac', models.CharField(serialize=False, primary_key=True, max_length=18)),
                ('physical_name', models.CharField(max_length=20)),
                ('pxe', models.ForeignKey(related_name='+', to='BluePrint.PXE')),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='ReservedAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
                ('reason', models.CharField(max_length=50)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='block',
            field=models.ForeignKey(to='Utilities.AddressBlock'),
        ),
        migrations.CreateModel(
            name='AggragatedNetworkInterface',
            fields=[
                ('abstractnetworkinterface_ptr', models.OneToOneField(to='Utilities.AbstractNetworkInterface', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
                ('paramaters', contractor.fields.MapField(default={})),
                ('master_interface', models.ForeignKey(related_name='+', to='Utilities.NetworkInterface')),
                ('slaves', models.ManyToManyField(related_name='_aggragatednetworkinterface_slaves_+', to='Utilities.NetworkInterface')),
            ],
            bases=('Utilities.abstractnetworkinterface',),
        ),
        migrations.AlterUniqueTogether(
            name='networked',
            unique_together=set([('site', 'hostname')]),
        ),
        migrations.AlterUniqueTogether(
            name='baseaddress',
            unique_together=set([('block', 'offset')]),
        ),
        migrations.AddField(
            model_name='address',
            name='networked',
            field=models.ForeignKey(to='Utilities.Networked'),
        ),
    ]
