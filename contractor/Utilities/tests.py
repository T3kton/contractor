import pytest

from django.core.exceptions import ValidationError

from contractor.lib.ip import StrToIp
from contractor.Utilities.models import Networked, AddressBlock, Network, NetworkAddressBlock, BaseAddress, Address, ReservedAddress, DynamicAddress, NetworkInterface
from contractor.Site.models import Site


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

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=2, vlan_tagged=False )
  nab2.full_clean()

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=2, vlan_tagged=True )
  nab2.full_clean()

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=0, vlan_tagged=False )
  nab2.full_clean()

  nab2 = NetworkAddressBlock( network=n1, address_block=ab1, vlan=0, vlan_tagged=True )
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
  assert ba1.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'auto': True, 'mtu': 1500 }

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
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=254 )
  ba.full_clean()
  assert ba.as_dict == { 'address': '0.0.0.254', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress( address_block=ab1, offset=255 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab2, offset=0 )
  ba.full_clean()
  assert ba.as_dict == { 'address': '1.0.0.0', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress( address_block=ab2, offset=1 )
  ba.full_clean()
  assert ba.as_dict == { 'address': '1.0.0.1', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

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
  assert ba.as_dict == { 'address': '2.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '2.0.0.0', 'gateway': '2.0.0.1', 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( pk=ba1.pk )
  assert ba.type == 'Unknown'
  assert ba.ip_address is None
  assert ba.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'auto': True, 'mtu': 1500 }


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
  assert ad1.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True, 'mtu': 1500 }

  ad1.address_block = ab2
  ad1.offset = 5
  ad1.save()
  assert ad1.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True, 'mtu': 1500 }

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
  assert ad.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True, 'mtu': 1500 }

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
  assert ad.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=2 )
  ba.full_clean()
  ba.save()
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ad = Address( address_block=ab1, offset=2, networked=nwd, interface_name='eth0' )
  with pytest.raises( ValidationError ):
    ad.full_clean()

  ad = Address( address_block=ab1, offset=3, networked=nwd, interface_name='lo' )
  ad.full_clean()

  ad = Address( address_block=ab2, offset=0, networked=nwd, interface_name='lo', alias_index=0 )
  with pytest.raises( ValidationError ):
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
  assert ad.as_dict == { 'address': '1.0.0.0', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': True, 'auto': True, 'mtu': 1500 }

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
  assert ad.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'Address'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( address_block=ab1, offset=2 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.2'
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ad = Address.objects.get( networked=nwd, interface_name='vpn0' )
  assert ad.type == 'Address'
  assert ad.ip_address == '1.0.0.5'
  assert ad.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( pk=ad.baseaddress_ptr.pk )
  assert ba.type == 'Address'
  assert ba.ip_address is None
  assert ba.subclass.ip_address == '1.0.0.5'
  assert ba.as_dict == { 'address': None, 'netmask': None, 'prefix': None, 'subnet': None, 'gateway': None, 'auto': True, 'mtu': 1500 }
  assert ba.subclass.as_dict == { 'address': '1.0.0.5', 'netmask': '255.255.255.254', 'prefix': 31, 'subnet': '1.0.0.0', 'gateway': None, 'alias_index': None, 'primary': False, 'auto': True, 'mtu': 1500 }


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
  assert ra.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=2 )
  ba.full_clean()
  ba.save()
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ra = ReservedAddress( address_block=ab1, offset=2, reason='testing' )
  with pytest.raises( ValidationError ):
    ra.full_clean()

  ra = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ra.type == 'ReservedAddress'
  assert ra.ip_address == '0.0.0.1'
  assert ra.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'ReservedAddress'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( address_block=ab1, offset=2 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.2'
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }


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
  assert da.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress( address_block=ab1, offset=1 )
  with pytest.raises( ValidationError ):
    ba.full_clean()

  ba = BaseAddress( address_block=ab1, offset=2 )
  ba.full_clean()
  ba.save()
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  da = DynamicAddress( address_block=ab1, offset=2 )
  with pytest.raises( ValidationError ):
    da.full_clean()

  da = DynamicAddress.objects.get( address_block=ab1, offset=1 )
  assert da.type == 'DynamicAddress'
  assert da.ip_address == '0.0.0.1'
  assert da.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( address_block=ab1, offset=1 )
  assert ba.type == 'DynamicAddress'
  assert ba.ip_address == '0.0.0.1'
  assert ba.as_dict == { 'address': '0.0.0.1', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }

  ba = BaseAddress.objects.get( address_block=ab1, offset=2 )
  assert ba.type == 'Unknown'
  assert ba.ip_address == '0.0.0.2'
  assert ba.as_dict == { 'address': '0.0.0.2', 'netmask': '255.255.255.0', 'prefix': 24, 'subnet': '0.0.0.0', 'gateway': None, 'auto': True, 'mtu': 1500 }
