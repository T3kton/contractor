# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import contractor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('BluePrint', '0001_initial'),
        ('Building', '0001_initial'),
        ('Site', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('subnet', contractor.fields.IpAddressField(editable=True)),
                ('prefix', models.IntegerField()),
                ('gateway_offset', models.IntegerField(null=True, blank=True)),
                ('_max_address', contractor.fields.IpAddressField(editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='BaseAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('offset', models.IntegerField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Networked',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('hostname', models.CharField(max_length=100)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('is_provisioning', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AbstractNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('interface_name', models.CharField(max_length=20)),
                ('sub_interface', models.IntegerField(null=True, default=None, blank=True)),
                ('vlan', models.IntegerField(default=0)),
                ('is_primary', models.BooleanField(default=False)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='DynamicAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('pxe', models.ForeignKey(null=True, blank=True, to='BluePrint.PXE', related_name='+')),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='RealNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(to='Utilities.NetworkInterface', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('mac', models.CharField(null=True, max_length=18, blank=True)),
                ('physical_location', models.CharField(max_length=100)),
                ('foundation', models.ForeignKey(related_name='networkinterface_set', to='Building.Foundation')),
                ('pxe', models.ForeignKey(null=True, blank=True, to='BluePrint.PXE', on_delete=django.db.models.deletion.PROTECT, related_name='+')),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='ReservedAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(to='Utilities.BaseAddress', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('reason', models.CharField(max_length=50)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='address_block',
            field=models.ForeignKey(null=True, blank=True, to='Utilities.AddressBlock'),
        ),
        migrations.CreateModel(
            name='AggregatedNetworkInterface',
            fields=[
                ('abstractnetworkinterface_ptr', models.OneToOneField(to='Utilities.AbstractNetworkInterface', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('paramaters', contractor.fields.MapField(default=contractor.fields.defaultdict)),
                ('master_interface', models.ForeignKey(related_name='+', to='Utilities.NetworkInterface')),
                ('slaves', models.ManyToManyField(related_name='_aggregatednetworkinterface_slaves_+', to='Utilities.NetworkInterface')),
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
        migrations.AlterUniqueTogether(
            name='addressblock',
            unique_together=set([('site', 'name')]),
        ),
        migrations.AddField(
            model_name='address',
            name='networked',
            field=models.ForeignKey(to='Utilities.Networked'),
        ),
        migrations.AddField(
            model_name='address',
            name='pointer',
            field=models.ForeignKey(null=True, blank=True, to='Utilities.Address', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
