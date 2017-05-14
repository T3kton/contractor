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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('offset', models.IntegerField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Networked',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('hostname', models.CharField(max_length=100)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Site.Site')),
            ],
        ),
        migrations.CreateModel(
            name='NetworkInterface',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AbstractNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='Utilities.NetworkInterface', primary_key=True)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='Utilities.BaseAddress', primary_key=True)),
                ('interface_name', models.CharField(max_length=20)),
                ('is_primary', models.BooleanField(default=False)),
                ('is_provisioning', models.BooleanField(default=False)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='DynamicAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='Utilities.BaseAddress', primary_key=True)),
                ('pxe', models.ForeignKey(related_name='+', to='BluePrint.PXE', blank=True, null=True)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.CreateModel(
            name='RealNetworkInterface',
            fields=[
                ('networkinterface_ptr', models.OneToOneField(auto_created=True, parent_link=True, to='Utilities.NetworkInterface')),
                ('mac', models.CharField(blank=True, unique=True, max_length=18, null=True)),
                ('pxe', models.ForeignKey(related_name='+', to='BluePrint.PXE', blank=True, null=True)),
            ],
            bases=('Utilities.networkinterface',),
        ),
        migrations.CreateModel(
            name='ReservedAddress',
            fields=[
                ('baseaddress_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='Utilities.BaseAddress', primary_key=True)),
                ('reason', models.CharField(max_length=50)),
            ],
            bases=('Utilities.baseaddress',),
        ),
        migrations.AddField(
            model_name='baseaddress',
            name='address_block',
            field=models.ForeignKey(to='Utilities.AddressBlock'),
        ),
        migrations.CreateModel(
            name='AggragatedNetworkInterface',
            fields=[
                ('abstractnetworkinterface_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='Utilities.AbstractNetworkInterface', primary_key=True)),
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
    ]
