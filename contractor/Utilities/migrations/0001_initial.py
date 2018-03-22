# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BluePrint', '0001_initial'),
        ('Site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBlock',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=40)),
                ('subnet', contractor.fields.IpAddressField()),
                ('prefix', models.IntegerField()),
                ('gateway_offset', models.IntegerField(blank=True, null=True)),
                ('_max_address', contractor.fields.IpAddressField(editable=False)),
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
                ('site', models.ForeignKey(to='Site.Site', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=20)),
                ('is_provisioning', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AbstractNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, auto_created=True, to='Utilities.NetworkInterface')),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, auto_created=True, to='Utilities.BaseAddress')),
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
                ('baseaddress_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, auto_created=True, to='Utilities.BaseAddress')),
                ('pxe', models.ForeignKey(null=True, related_name='+', to='BluePrint.PXE', blank=True)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='RealNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, auto_created=True, to='Utilities.NetworkInterface')),
                ('mac', models.CharField(max_length=18, blank=True, null=True, unique=True)),
                ('pxe', models.ForeignKey(null=True, related_name='+', to='BluePrint.PXE', blank=True)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='ReservedAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, auto_created=True, to='Utilities.BaseAddress')),
                ('reason', models.CharField(max_length=50)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='address_block',
            field=models.ForeignKey(null=True, to='Utilities.AddressBlock', blank=True),
        ),
        migrations.CreateModel(
            name='AggragatedNetworkInterface',
            fields=[
                ('abstractnetworkinterface_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, auto_created=True, to='Utilities.AbstractNetworkInterface')),
                ('paramaters', contractor.fields.MapField(default={})),
                ('master_interface', models.ForeignKey(to='Utilities.NetworkInterface', related_name='+')),
                ('slaves', models.ManyToManyField(to='Utilities.NetworkInterface', related_name='_aggragatednetworkinterface_slaves_+')),
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
            field=models.ForeignKey(null=True, to='Utilities.Address', blank=True),
        ),
    ]
