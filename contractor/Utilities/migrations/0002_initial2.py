# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('BluePrint', '0001_initial'),
        ('Building', '0002_initial2'),
        ('Site', '0001_initial'),
        ('Utilities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=40)),
                ('subnet', contractor.fields.IpAddressField(editable=True)),
                ('prefix', models.IntegerField()),
                ('gateway_offset', models.IntegerField(null=True, blank=True)),
                ('_max_address', contractor.fields.IpAddressField(editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(to='Site.Site', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='BaseAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('offset', models.IntegerField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={'default_permissions': ()},
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('mtu', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='NetworkAddressBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('vlan', models.IntegerField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('address_block', models.ForeignKey(to='Utilities.AddressBlock',on_delete=models.CASCADE)),
                ('network', models.ForeignKey(to='Utilities.Network',on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=20)),
                ('is_provisioning', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={'default_permissions': ()},
        ),
        migrations.CreateModel(
            name='AbstractNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', parent_link=True, serialize=False, primary_key=True, auto_created=True,on_delete=models.CASCADE)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', parent_link=True, serialize=False, primary_key=True, auto_created=True,on_delete=models.CASCADE)),
                ('interface_name', models.CharField(max_length=20)),
                ('alias_index', models.IntegerField(null=True, default=None, blank=True)),
                ('is_primary', models.BooleanField(default=False)),
                ('networked', models.ForeignKey(to='Utilities.Networked',on_delete=models.CASCADE)),
                ('pointer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Utilities.Address', null=True, blank=True)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='DynamicAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', parent_link=True, serialize=False, primary_key=True, auto_created=True,on_delete=models.CASCADE)),
                ('pxe', models.ForeignKey(to='BluePrint.PXE', null=True, blank=True, related_name='+',on_delete=models.CASCADE)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='RealNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', parent_link=True, serialize=False, primary_key=True, auto_created=True,on_delete=models.CASCADE)),
                ('mac', models.CharField(max_length=18, blank=True, null=True)),
                ('physical_location', models.CharField(max_length=100)),
                ('link_name', models.CharField(max_length=100, blank=True, null=True)),
                ('foundation', models.ForeignKey(to='Building.Foundation', related_name='networkinterface_set',on_delete=models.CASCADE)),
                ('pxe', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='BluePrint.PXE', null=True, blank=True, related_name='+')),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='ReservedAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', parent_link=True, serialize=False, primary_key=True, auto_created=True,on_delete=models.CASCADE)),
                ('reason', models.CharField(max_length=50)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.AddField(
            model_name='networkinterface',
            name='network',
            field=models.ForeignKey(to='Utilities.Network', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='network',
            name='address_block_list',
            field=models.ManyToManyField(to='Utilities.AddressBlock', through='Utilities.NetworkAddressBlock'),
        ),
        migrations.AddField(
            model_name='network',
            name='site',
            field=models.ForeignKey(to='Site.Site', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='address_block',
            field=models.ForeignKey(to='Utilities.AddressBlock', null=True, blank=True,on_delete=models.CASCADE),
        ),
        migrations.CreateModel(
            name='AggregatedNetworkInterface',
            fields=[
                ('abstractnetworkinterface_ptr', models.OneToOneField(to='Utilities.AbstractNetworkInterface', parent_link=True, serialize=False, primary_key=True, auto_created=True,on_delete=models.CASCADE)),
                ('paramaters', contractor.fields.MapField(default=contractor.fields.defaultdict)),
                ('master_interface', models.ForeignKey(to='Utilities.NetworkInterface', related_name='+',on_delete=models.CASCADE)),
                ('slaves', models.ManyToManyField(to='Utilities.NetworkInterface', related_name='_aggregatednetworkinterface_slaves_+')),
            ],
            bases=('Utilities.abstractnetworkinterface',),
        ),
        migrations.AlterUniqueTogether(
            name='network',
            unique_together=set([('site', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='baseaddress',
            unique_together=set([('address_block', 'offset')]),
        ),
        migrations.AlterUniqueTogether(
            name='addressblock',
            unique_together=set([('site', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='realnetworkinterface',
            unique_together=set([('foundation', 'physical_location')]),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('interface_name', 'alias_index')]),
        ),
    ]
