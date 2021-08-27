import pytest

from django.db import transaction
from django.core.exceptions import ValidationError

from contractor.lib.ip import StrToIp
from contractor.Utilities.models import Networked, AddressBlock, Network, NetworkAddressBlock, BaseAddress, Address, ReservedAddress, DynamicAddress, NetworkInterface, RealNetworkInterface, AbstractNetworkInterface, AggregatedNetworkInterface
from contractor.Site.models import Site
from contractor.BluePrint.models import FoundationBluePrint, StructureBluePrint
from contractor.Building.models import Foundation, Structure


@pytest.mark.django_db
def test_networked():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  nwd = Networked()
  with pytest.raises( ValidationError ):
    nwd.full_clean()

  nwd = Networked( hostname='sdf' )
  with pytest.raises( ValidationError ):
    nwd.full_clean()

  nwd = Networked( site=s1, hostname='test' )
  nwd.full_clean()
  nwd.save()

  nwd = Networked( site=s1, hostname='test' )
  with pytest.raises( ValidationError ):
    nwd.full_clean()

  nwd = Networked( site=s1, hostname='bad.host' )
  with pytest.raises( ValidationError ):
    nwd.full_clean()


@pytest.mark.django_db
def test_addressblock():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  s2 = Site( name='tsite2', description='test site2' )
  s2.full_clean()
  s2.save()

  ab = AddressBlock()
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ) )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24, name='test' )
  ab.full_clean()
  ab.save()

  ab.gateway_offset = 1
  ab.full_clean()
  ab.save()

  ab.name = 'something_else'
  ab.full_clean()
  ab.save()

  ab.name = 'test'
  ab.full_clean()
  ab.save()

  ab = AddressBlock( site=s1, subnet=StrToIp( '50.0.0.0' ), prefix=24, name='test' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s2, subnet=StrToIp( '51.0.0.0' ), prefix=24, name='test' )
  ab.full_clean()
  ab.save()

  ab.site = s1
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab.site = s2
  ab.full_clean()
  ab.save()

  ab = AddressBlock.objects.get( site=s1, name='test' )
  ab.gateway_offset = None
  ab.full_clean()
  ab.save()

  ab = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24, name='test2' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s2, subnet=StrToIp( '0.0.0.0' ), prefix=24, name='test2' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=24, name='test3' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=-1, name='test4' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=33, name='test5' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '255.0.0.0' ), prefix=1, name='test6' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32, name='test7' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '2.0.0.0' ), prefix=8, gateway_offset=1, name='test8' )
  ab.full_clean()
  ab.save()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=24, gateway_offset=1, name='test9' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32, gateway_offset=0, name='test10' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32, gateway_offset=1, name='test11' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32, gateway_offset=2, name='test12' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, gateway_offset=0, name='test13' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, gateway_offset=1, name='test14' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, gateway_offset=2, name='test15' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=0, name='test16' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=1, name='test17' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=2, name='test18' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=3, name='test19' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=0, name='test20' )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=1, name='test21' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=2, name='test22' )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=3, name='test23' )
  ab.full_clean()

  ab = AddressBlock.objects.get( site=s1, name='test' )
  assert ab.subnet == '0.0.0.0'
  assert ab._max_address == '0.0.0.255'
  assert ab.gateway is None
  assert ab.netmask == '255.255.255.0'
  assert ab.prefix == 24
  assert ab.size == 254
  assert ab.offsetBounds == ( 1, 254 )
  assert ab.isIpV4 is True

  ab = AddressBlock.objects.get( site=s1, name='test8' )
  assert ab.subnet == '2.0.0.0'
  assert ab._max_address == '2.255.255.255'
  assert ab.gateway == '2.0.0.1'
  assert ab.netmask == '255.0.0.0'
  assert ab.prefix == 8
  assert ab.size == 16777214
  assert ab.offsetBounds == ( 1, 16777214 )
  assert ab.isIpV4 is True

  ab = AddressBlock( site=s1, subnet=StrToIp( '10.0.0.0' ), prefix=24, name='test30' )
  ab.full_clean()
  ab.save()

  ab = AddressBlock( site=s1, subnet='11.0.0.0', prefix=24, name='test31' )
  ab.full_clean()
  ab.save()

  ab = AddressBlock.objects.get( name='test30' )
  assert ab.subnet == '10.0.0.0'
  assert ab._max_address == '10.0.0.255'
  assert ab.gateway is None
  assert ab.netmask == '255.255.255.0'
  assert ab.prefix == 24
  assert ab.size == 254
  assert ab.offsetBounds == ( 1, 254 )
  assert ab.isIpV4 is True

  ab = AddressBlock.objects.get( name='test31' )
  assert ab.subnet == '11.0.0.0'
  assert ab._max_address == '11.0.0.255'
  assert ab.gateway is None
  assert ab.netmask == '255.255.255.0'
  assert ab.prefix == 24
  assert ab.size == 254
  assert ab.offsetBounds == ( 1, 254 )
  assert ab.isIpV4 is True

  # TODO: test ipv6

@pytest.mark.django_db
def test_addressblock_resize():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  ab = AddressBlock( site=s1, name='boundless', subnet='10.0.0.0', prefix=26 )
  ab.full_clean()
  ab.save()

  for offset in ( 2, 10, 20, 50, 61 ):
    ba = BaseAddress( address_block=ab, offset=offset )
    ba.full_clean()
    ba.save()

  ab.prefix = 25
  ab.full_clean()
  ab.save()

  for offset in ( 3, 11, 21, 51, 63, 100, 120, 124 ):
    ba = BaseAddress( address_block=ab, offset=offset )
    ba.full_clean()
    ba.save()

  ab.prefix = 26
  with pytest.raises( ValidationError ):
    ab.full_clean()


@pytest.mark.django_db
def test_network():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  ab1 = AddressBlock( site=s1, subnet=StrToIp( '10.0.0.0' ), prefix=24, name='test' )
  ab1.full_clean()
  ab1.save()

  n1 = Network()
  with pytest.raises( ValidationError ):
    n1.full_clean()

  n1 = Network( name='test', site=s1 )
  n1.full_clean()
  n1.save()

  n2 = Network( name='test', site=s1 )
  with pytest.raises( ValidationError ):
    n2.full_clean()

  nab1 = NetworkAddressBlock( network=n1, address_block=ab1 )
  nab1.full_clean()
  nab1.save()

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=0 )
  nab2.full_clean()

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=1 )
  nab2.full_clean()

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=-1 )
  with pytest.raises( ValidationError ):
    nab2.full_clean()

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=4097 )
  with pytest.raises( ValidationError ):
    nab2.full_clean()


@pytest.mark.django_db
def test_networkinterface():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  n1 = Network( name='test', site=s1 )
  n1.full_clean()
  n1.save()

  ni1 = NetworkInterface()
  with pytest.raises( ValidationError ):
    ni1.full_clean()

  ni1 = NetworkInterface( name='eth0', network=n1 )
  ni1.full_clean()
  ni1.save()

  ni2 = NetworkInterface( name='3 d', network=n1 )
  with pytest.raises( ValidationError ):
    ni2.full_clean()

  assert ni1.config == { 'name': 'eth0', 'network': 'test', 'address_list': [] }


@pytest.mark.django_db
def test_realnetworkinterface():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  n1 = Network( name='test', site=s1 )
  n1.full_clean()
  n1.save()

  fb = FoundationBluePrint( name='testing', description='testing', foundation_type_list=[ 'Unknown' ] )
  fb.full_clean()
  fb.save()

  f1 = Foundation( locator='testf', site=s1, blueprint=fb )
  f1.full_clean()
  f1.save()

  ri1 = RealNetworkInterface()
  with pytest.raises( ValidationError ):
    ri1.full_clean()

  ri1 = RealNetworkInterface( name='eth0', network=n1 )
  with pytest.raises( ValidationError ):
    ri1.full_clean()

  ri1 = RealNetworkInterface( name='ba d', network=n1, foundation=f1, physical_location='eth0' )
  with pytest.raises( ValidationError ):
    ri1.full_clean()

  ri1 = RealNetworkInterface( name='eno1', network=n1, foundation=f1, physical_location='eth0' )
  ri1.full_clean()
  ri1.save()

  assert ri1.config == { 'name': 'eno1', 'network': 'test', 'address_list': [], 'physical_location': 'eth0', 'mac': None, 'link_name': None }

  ri2 = RealNetworkInterface( name='eno2', network=n1, foundation=f1, physical_location='eth0' )
  with pytest.raises( ValidationError ):
    ri2.full_clean()

  ri2.physical_location = 'eth1'
  ri2.full_clean()

  assert ri2.config == { 'name': 'eno2', 'network': 'test', 'address_list': [], 'physical_location': 'eth1', 'mac': None, 'link_name': None }

  ri2.mac = '11:22:33:4D:55:66'
  ri2.full_clean()

  assert ri2.config == { 'name': 'eno2', 'network': 'test', 'address_list': [], 'physical_location': 'eth1', 'mac': '11:22:33:4d:55:66', 'link_name': None }

  ri2.mac = 'b211.1234.4433'
  ri2.full_clean()

  assert ri2.config == { 'name': 'eno2', 'network': 'test', 'address_list': [], 'physical_location': 'eth1', 'mac': 'b2:11:12:34:44:33', 'link_name': None }

  ri2.mac = '12a123123123'
  ri2.full_clean()

  assert ri2.config == { 'name': 'eno2', 'network': 'test', 'address_list': [], 'physical_location': 'eth1', 'mac': '12:a1:23:12:31:23', 'link_name': None }

  for mac in ( '12:3123123123', '11:22:33:44:55:s6', '2211.12z4.4433', 'sdf', '22:11:12:34.4433' ):
    ri2.mac = mac
    with pytest.raises( ValidationError ):
      ri2.full_clean()

  ri1.is_provisioning = True
  ri1.full_clean()
  ri1.save()

  ri2.is_provisioning = True
  with pytest.raises( ValidationError ):
    ri2.full_clean()


@pytest.mark.django_db
def test_abstractnetworkinterface():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  n1 = Network( name='test', site=s1 )
  n1.full_clean()
  n1.save()

  fb = FoundationBluePrint( name='testing', description='testing', foundation_type_list=[ 'Unknown' ] )
  fb.full_clean()
  fb.save()

  sb = StructureBluePrint( name='testing2', description='testing2' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  f1 = Foundation( locator='testf', site=s1, blueprint=fb )
  f1.full_clean()
  f1.save()

  s1 = Structure( hostname='tests', foundation=f1, blueprint=sb, site=s1 )
  s1.full_clean()
  s1.save()

  ai1 = AbstractNetworkInterface()
  with pytest.raises( ValidationError ):
    ai1.full_clean()

  ai1 = AbstractNetworkInterface( structure=s1, name='dmz', network=n1 )
  ai1.full_clean()
  ai1.save()

  assert ai1.config == { 'address_list': [], 'name': 'dmz', 'network': 'test' }

  ai2 = AbstractNetworkInterface( structure=s1, name='dmz', network=n1 )
  with pytest.raises( ValidationError ):
    ai2.full_clean()

  ai2 = AbstractNetworkInterface( structure=s1, name='external', network=n1 )
  ai2.full_clean()


@pytest.mark.django_db
def test_aggergatednetworkinterface():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  n1 = Network( name='test', site=s1 )
  n1.full_clean()
  n1.save()

  fb = FoundationBluePrint( name='testing', description='testing', foundation_type_list=[ 'Unknown' ] )
  fb.full_clean()
  fb.save()

  sb = StructureBluePrint( name='testing2', description='testing2' )
  sb.full_clean()
  sb.save()
  sb.foundation_blueprint_list.add( fb )

  f1 = Foundation( locator='testf', site=s1, blueprint=fb )
  f1.full_clean()
  f1.save()

  primary = RealNetworkInterface( foundation=f1, name='ens1', physical_location='eth0', network=n1 )
  primary.full_clean()
  primary.save()

  secondary1 = RealNetworkInterface( foundation=f1, name='ens2', physical_location='eth1', network=n1 )
  secondary1.full_clean()
  secondary1.save()

  secondary2 = RealNetworkInterface( foundation=f1, name='ens3', physical_location='eth2', network=n1 )
  secondary2.full_clean()
  secondary2.save()

  f2 = Foundation( locator='testf2', site=s1, blueprint=fb )
  f2.full_clean()
  f2.save()

  primary_2 = RealNetworkInterface( foundation=f2, name='ens1', physical_location='eth0', network=n1 )
  primary_2.full_clean()
  primary_2.save()

  secondary1_2 = RealNetworkInterface( foundation=f2, name='ens2', physical_location='eth1', network=n1 )
  secondary1_2.full_clean()
  secondary1_2.save()

  st1 = Structure( hostname='tests', foundation=f1, blueprint=sb, site=s1 )
  st1.full_clean()
  st1.save()

  a_primary = AbstractNetworkInterface( structure=st1, name='aeth0', network=n1 )
  a_primary.full_clean()
  a_primary.save()

  a_secondary = AbstractNetworkInterface( structure=st1, name='aeth1', network=n1 )
  a_secondary.full_clean()
  a_secondary.save()

  st2 = Structure( hostname='tests2', foundation=f2, blueprint=sb, site=s1 )
  st2.full_clean()
  st2.save()

  a_primary_2 = AbstractNetworkInterface( structure=st2, name='aeth0', network=n1 )
  a_primary_2.full_clean()
  a_primary_2.save()

  a_secondary_2 = AbstractNetworkInterface( structure=st2, name='aeth1', network=n1 )
  a_secondary_2.full_clean()
  a_secondary_2.save()

  ai1 = AggregatedNetworkInterface()
  with pytest.raises( ValidationError ):
    ai1.full_clean()

  ai1 = AggregatedNetworkInterface( structure=st1, name='dmz', network=n1, primary_interface=primary )
  ai1.full_clean()
  ai1.save()
  ai1.full_clean()  # test the self.pk part of clean

  assert ai1.config == { 'address_list': [], 'name': 'dmz', 'network': 'test', 'primary': 'ens1', 'secondary': [] }

  ai2 = AggregatedNetworkInterface( structure=st1, name='dmz', network=n1, primary_interface=primary )
  with pytest.raises( ValidationError ):
    ai2.full_clean()

  ai2 = AggregatedNetworkInterface( structure=st1, name='external', network=n1, primary_interface=primary )
  ai2.full_clean()
  ai2.save()

  ai1.secondary_interfaces.add( secondary1 )

  assert ai1.config == { 'address_list': [], 'name': 'dmz', 'network': 'test', 'primary': 'ens1', 'secondary': [ 'ens2' ] }

  ai1.secondary_interfaces.add( secondary2 )

  assert ai1.config == { 'address_list': [], 'name': 'dmz', 'network': 'test', 'primary': 'ens1', 'secondary': [ 'ens2', 'ens3' ] }

  with transaction.atomic():  # b/c we throw an exception in m2m_change, the transaction dosen't close, we have to force this ourselves
    with pytest.raises( ValidationError ):
      ai1.secondary_interfaces.add( primary )

  ai1.full_clean()

  ai1.primary_interface = secondary1
  with pytest.raises( ValidationError ):
    ai1.full_clean()

  ai2.primary_interface = primary
  ai2.full_clean()

  ai2.primary_interface = primary_2
  with pytest.raises( ValidationError ):
    ai2.full_clean()

  ai2.primary_interface = a_primary_2
  with pytest.raises( ValidationError ):
    ai2.full_clean()

  ai2.primary_interface = a_primary
  ai2.full_clean()

  ai2.secondary_interfaces.add( secondary1 )

  with transaction.atomic():
    with pytest.raises( ValidationError ):
      ai2.secondary_interfaces.add( secondary1_2 )

  ai2.full_clean()

  ai2.secondary_interfaces.add( a_secondary )

  with transaction.atomic():
    with pytest.raises( ValidationError ):
      ai2.secondary_interfaces.add( a_secondary_2 )


@pytest.mark.django_db
def test_baseaddress():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  ab1 = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24, name='test1' )
  ab1.full_clean()
  ab1.save()

  ab2 = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, name='test2' )
  ab2.full_clean()
  ab2.save()

  ab3 = AddressBlock( site=s1, subnet=StrToIp( '2.0.0.0' ), prefix=24, gateway_offset=1, name='test3' )
  ab3.full_clean()
  ab3.save()

  ba1 = BaseAddress()
  ba1.full_clean()
  ba1.save()
  assert ba1.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'auto': True }

  ba = BaseAddress( address_block=ab1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( offset=0 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=0 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=1 )
  ba.full_clean()
  ba.save()
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=254 )
  ba.full_clean()
  assert ba.as_dict == { 'address': '0.0.0.254', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress( address_block=ab1, offset=255 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab2, offset=0 )
  ba.full_clean()
  assert ba.as_dict == { 'address': '1.0.0.0', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress( address_block=ab2, offset=1 )
  ba.full_clean()
  assert ba.as_dict == { 'address': '1.0.0.1', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress( address_block=ab2, offset=2 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab2, offset=-1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab3, offset=0 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab3, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab3, offset=2 )
  ba.full_clean()
  assert ba.as_dict == { 'address': '2.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '2.0.0.0', 'gateway': '2.0.0.1', 'auto': True }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress.objects.get( pk=ba1.pk )
  assert ba.type == 'Unknown'
  assert ba.ip_address is None
  assert ba.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'auto': True }


@pytest.mark.django_db
def test_baseaddress_lookup():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  s2 = Site( name='tsite2', description='test site2' )
  s2.full_clean()
  s2.save()

  ab11 = AddressBlock( site=s1, subnet=StrToIp( '10.0.0.0' ), prefix=12, name='test11' )
  ab11.full_clean()
  ab11.save()

  ab12 = AddressBlock( site=s1, subnet=StrToIp( '192.168.0.0' ), prefix=24, name='test12' )
  ab12.full_clean()
  ab12.save()

  ab13 = AddressBlock( site=s1, subnet=StrToIp( '1.2.3.0' ), prefix=24, name='test13' )
  ab13.full_clean()
  ab13.save()

  ab21 = AddressBlock( site=s2, subnet=StrToIp( '10.0.0.0' ), prefix=24, name='test21' )
  ab21.full_clean()
  ab21.save()

  ab22 = AddressBlock( site=s2, subnet=StrToIp( '192.168.0.0' ), prefix=24, name='test22' )
  ab22.full_clean()
  ab22.save()

  ab23 = AddressBlock( site=s2, subnet=StrToIp( '10.0.1.0' ), prefix=24, name='test23' )
  ab23.full_clean()
  ab23.save()

  for ab, offset in [ ( ab11, 10 ), ( ab12, 10 ), ( ab13, 10 ), ( ab21, 10 ), ( ab22, 10 ), ( ab12, 42 ), ( ab12, 22 ), ( ab11, 266 ), ( ab23, 10 ) ]:
    ba = BaseAddress( address_block=ab, offset=offset )
    print( ba.ip_address )
    ba.full_clean()
    ba.save()

  assert BaseAddress.lookup( '1.1.1' ) is None
  assert BaseAddress.lookup( 'asdf' ) is None

  assert BaseAddress.lookup( '1.1.1.1' ) is None
  assert BaseAddress.lookup( '10.1.1.1' ) is None
  assert BaseAddress.lookup( '10.0.1.1' ) is None
  assert BaseAddress.lookup( '10.0.0.1' ) is None

  assert BaseAddress.lookup( '1.1.1.10' ) is None
  assert BaseAddress.lookup( '10.1.1.10' ) is None
  assert BaseAddress.lookup( '10.0.1.10' ) is None

  assert BaseAddress.lookup( '10.0.0.10' ) is None

  ba = BaseAddress.lookup( '10.0.0.10', site=s1 )
  assert ba.address_block == ab11
  assert ba.offset == 10

  ba = BaseAddress.lookup( '10.0.0.10', site=s2 )
  assert ba.address_block == ab21
  assert ba.offset == 10

  ba = BaseAddress.lookup( '1.2.3.10' )
  assert ba.address_block == ab13
  assert ba.offset == 10

  ba = BaseAddress.lookup( '1.2.3.10', site=s1 )
  assert ba.address_block == ab13
  assert ba.offset == 10

  assert BaseAddress.lookup( '1.2.3.10', site=s2 ) is None

  assert BaseAddress.lookup( '10.0.1.10' ) is None

  ba = BaseAddress.lookup( '10.0.1.10', site=s1 )
  assert ba.address_block == ab11
  assert ba.offset == 266

  ba = BaseAddress.lookup( '10.0.1.10', site=s2 )
  assert ba.address_block == ab23
  assert ba.offset == 10


@pytest.mark.django_db
def test_address():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  nwd = Networked( site=s1, hostname='test' )
  nwd.full_clean()
  nwd.save()

  ab1 = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24, name='test1' )
  ab1.full_clean()
  ab1.save()

  ab2 = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, name='test2' )
  ab2.full_clean()
  ab2.save()

  ad = Address()
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad1 = Address( networked=nwd, interface_name='tun0' )
  ad1.full_clean()
  ad1.save()
  assert ad1.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True }

  ad1.address_block = ab2
  ad1.offset = 5
  ad1.save()
  assert ad1.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True }

  ad = Address( address_block=ab1 )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab1, offset=1, networked=nwd )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab1, offset=1, networked=nwd, interface_name='lo' )
  ad.full_clean()
  ad.save()
  assert ad.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True }

  ad = Address( address_block=ab1, offset=1, pointer=ad1, networked=nwd, interface_name='vpn0' )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( offset=1, pointer=ad1, networked=nwd, interface_name='vpn0' )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab1, pointer=ad1, networked=nwd, interface_name='vpn0' )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab1, pointer=ad1, networked=nwd, interface_name='vpn0' )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( offset=1, pointer=ad1, networked=nwd, interface_name='vpn0' )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( pointer=ad1, networked=nwd, interface_name='vpn0' )
  ad.full_clean()
  ad.save()
  assert ad.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=2 )
  ba.full_clean()
  ba.save()
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ad = Address( address_block=ab1, offset=2, networked=nwd, interface_name='eth0' )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab1, offset=3, networked=nwd, interface_name='lo' )
  ad.full_clean()

  ad = Address( address_block=ab2, offset=0, networked=nwd, interface_name='lo', alias_index=0 )
  ad.full_clean()

  ad = Address( address_block=ab2, offset=0, networked=nwd, interface_name='lo', alias_index=1 )
  ad.full_clean()

  ad = Address( address_block=ab2, offset=0, networked=nwd, interface_name='lo', alias_index=123 )
  ad.full_clean()

  ad = Address( address_block=ab2, offset=0, networked=nwd, interface_name='lo', alias_index=-1 )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab2, offset=0, networked=nwd, interface_name='lo', is_primary=True )
  ad.full_clean()
  ad.save()
  assert ad.as_dict == { 'address': '1.0.0.0', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': True, 'auto': True }

  ad = Address( address_block=ab2, offset=1, networked=nwd, interface_name='lo', is_primary=True )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab2, offset=1, networked=nwd, interface_name='lo', is_primary=False )
  ad.full_clean()

  ad = Address.objects.get( address_block=ab1, offset=1 )
  assert ad.type == 'Address'
  assert ad.ip_address == '0.0.0.1'
  assert ad.structure is None   # TODO: make a networked with a structure and test that
  assert ad.interface is None   # TODO: dido ^
  assert ad.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'Address'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress.objects.get( address_block=ab1, offset=2 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.2'
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ad = Address.objects.get( networked=nwd, interface_name='vpn0' )
  assert ad.type == 'Address'
  assert ad.ip_address == '1.0.0.5'
  assert ad.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True }

  ba = BaseAddress.objects.get( pk=ad.baseaddress_ptr.pk )
  assert ba.type == 'Address'
  assert ba.ip_address is None
  assert ba.subclass.ip_address == '1.0.0.5'
  assert ba.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'auto': True }
  assert ba.subclass.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True }


@pytest.mark.django_db
def test_address_fromIpAddress():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  s2 = Site( name='tsite2', description='test site2' )
  s2.full_clean()
  s2.save()

  ab1 = AddressBlock( site=s1, subnet=StrToIp( '10.0.0.0' ), prefix=20, name='test1' )
  ab1.full_clean()
  ab1.save()

  ab2 = AddressBlock( site=s1, subnet=StrToIp( '192.168.0.0' ), prefix=24, name='test2' )
  ab2.full_clean()
  ab2.save()

  ab3 = AddressBlock( site=s2, subnet=StrToIp( '10.0.0.0' ), prefix=20, name='test3' )
  ab3.full_clean()
  ab3.save()

  assert Address.fromIPAddress( s1, '1.1.1' ) is None
  assert Address.fromIPAddress( s1, 'asdf' ) is None

  a = Address.fromIPAddress( s1, '10.0.0.10' )
  assert a.address_block == ab1
  assert a.offset == 10

  a = Address.fromIPAddress( s1, '10.0.1.10' )
  assert a.address_block == ab1
  assert a.offset == 266

  a = Address.fromIPAddress( s2, '10.0.0.10' )
  assert a.address_block == ab3
  assert a.offset == 10

  a = Address.fromIPAddress( s2, '10.0.1.10' )
  assert a.address_block == ab3
  assert a.offset == 266

  assert Address.fromIPAddress( s1, '10.3.0.10' ) is None
  assert Address.fromIPAddress( s1, '1.2.3.4' ) is None

  a = Address.fromIPAddress( s1, '192.168.0.5' )
  assert a.address_block == ab2
  assert a.offset == 5

  assert Address.fromIPAddress( s1, '192.168.1.5' ) is None


@pytest.mark.django_db
def test_reservedaddress():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  nwd = Networked( site=s1, hostname='test' )
  nwd.full_clean()
  nwd.save()

  ab1 = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24, name='test1' )
  ab1.full_clean()
  ab1.save()

  ab2 = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, name='test2' )
  ab2.full_clean()
  ab2.save()

  ra = ReservedAddress()
  with pytest.raises( ValidationError ):
    ra.full_clean()

  ra = ReservedAddress( reason='testing' )
  with pytest.raises( ValidationError ):
    ra.full_clean()

  ra = ReservedAddress( address_block=ab1 )
  with pytest.raises( ValidationError ):
    ra.full_clean()

  ra = ReservedAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ra.full_clean()

  ra = ReservedAddress( address_block=ab1, offset=1, reason='testing' )
  ra.full_clean()
  ra.save()
  assert ra.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=2 )
  ba.full_clean()
  ba.save()
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ra = ReservedAddress( address_block=ab1, offset=2, reason='testing' )
  with pytest.raises( ValidationError ):
    ra.full_clean()

  ra = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ra.type == 'ReservedAddress'
  assert ra.ip_address == '0.0.0.1'
  assert ra.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'ReservedAddress'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress.objects.get( address_block=ab1, offset=2 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.2'
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }


@pytest.mark.django_db
def test_dynamicaddress():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  nwd = Networked( site=s1, hostname='test' )
  nwd.full_clean()
  nwd.save()

  ab1 = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24, name='test1' )
  ab1.full_clean()
  ab1.save()

  ab2 = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, name='test2' )
  ab2.full_clean()
  ab2.save()

  da = DynamicAddress()
  with pytest.raises( ValidationError ):
    da.full_clean()

  da = DynamicAddress( address_block=ab1 )
  with pytest.raises( ValidationError ):
    da.full_clean()

  da = DynamicAddress( address_block=ab1, offset=1 )  # TODO: test with PXE set
  da.full_clean()
  da.save()
  assert da.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=2 )
  ba.full_clean()
  ba.save()
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  da = DynamicAddress( address_block=ab1, offset=2 )
  with pytest.raises( ValidationError ):
    da.full_clean()

  da = DynamicAddress.objects.get( address_block=ab1, offset=1 )
  assert da.type == 'DynamicAddress'
  assert da.ip_address == '0.0.0.1'
  assert da.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'DynamicAddress'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }

  ba = BaseAddress.objects.get( address_block=ab1, offset=2 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.2'
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True }
