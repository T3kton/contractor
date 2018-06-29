# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('BluePrint', '0001_initial'),
        ('Site', '0001_initial'),
        ('Building', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBlock',
            fields=[
                ('name', models.CharField(serialize=False, max_length=40, primary_key=True)),
                ('subnet', contractor.fields.IpAddressField()),
                ('prefix', models.IntegerField()),
                ('gateway_offset', models.IntegerField(blank=True, null=True)),
                ('_max_address', contractor.fields.IpAddressField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='BaseAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('offset', models.IntegerField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Networked',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('hostname', models.CharField(max_length=100)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('is_provisioning', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AbstractNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.NetworkInterface', serialize=False)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.BaseAddress', serialize=False)),
                ('interface_name', models.CharField(max_length=20)),
                ('sub_interface', models.IntegerField(blank=True, null=True, default=None)),
                ('vlan', models.IntegerField(default=0)),
                ('is_primary', models.BooleanField(default=False)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='DynamicAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.BaseAddress', serialize=False)),
                ('pxe', models.ForeignKey(to='BluePrint.PXE', blank=True, null=True, related_name='+')),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='RealNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.NetworkInterface', serialize=False)),
                ('mac', models.CharField(blank=True, null=True, max_length=18)),
                ('physical_location', models.CharField(max_length=100)),
                ('foundation', models.ForeignKey(related_name='networkinterface_set', to='Building.Foundation')),
                ('pxe', models.ForeignKey(to='BluePrint.PXE', blank=True, null=True, related_name='+')),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='ReservedAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.BaseAddress', serialize=False)),
                ('reason', models.CharField(max_length=50)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='address_block',
            field=models.ForeignKey(to='Utilities.AddressBlock', blank=True, null=True),
        ),
        migrations.CreateModel(
            name='AggragatedNetworkInterface',
            fields=[
                ('abstractnetworkinterface_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, to='Utilities.AbstractNetworkInterface', serialize=False)),
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
            unique_together=set([('address_block', 'offset')]),
        ),
        migrations.AddField(
            model_name='address',
            name='networked',
            field=models.ForeignKey(to='Utilities.Networked'),
        ),
        migrations.AddField(
            model_name='address',
            name='pointer',
            field=models.ForeignKey(to='Utilities.Address', blank=True, null=True),
        ),
    ]
