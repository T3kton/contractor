import re
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, IpAddressField, hostname_regex, name_regex
from contractor.BluePrint.models import PXE
from contractor.Site.models import Site
from contractor.lib.ip import IpIsV4, CIDRNetworkBounds, StrToIp, IpToStr, CIDRNetworkSize, CIDRNetmask

cinp = CInP( 'Utilities', '0.1' )


def ipAddress2Native( ip_address ):
  try:
    address_block = AddressBlock.objects.get( subnet__lte=ip_address, _max_address__gte=ip_address )
  except AddressBlock.DoesNotExist:
    raise ValueError( 'ip_address "{0}" does not exist in any existing Address Blocks'.format( ip_address ) )

  return address_block, StrToIp( ip_address ) - StrToIp( address_block.subnet )


@cinp.model( )
class Networked( models.Model ):
  hostname = models.CharField( max_length=100 )
  site = models.ForeignKey( Site, on_delete=models.PROTECT )

  @property
  def subclass( self ):
    try:
      return self.structure
    except AttributeError:
      pass

    return self

  @property
  def primary_ip( self ):
    try:
      return self.address_set.get( is_primary=True ).ip_address
    except Address.DoesNotExist:
      return None

  @property
  def provisioning_ip( self ):
    try:
      interface_name = self.foundation.interfaces.get( is_provisioning=True ).name
    except NetworkInterface.DoesNotExist:
      return None

    try:
      return self.address_set.get( interface_name=interface_name, is_primary=True ).ip_address
    except Address.DoesNotExist:
      return None

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not hostname_regex.match( self.hostname ):
      errors[ 'hostname' ] = 'Structure hostname "{0}" is invalid'.format( self.hostname )

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'site', 'hostname' ), )

  def __str__( self ):
    return 'Networked hostname "{0}" in "{1}"'.format( self.hostname, self.site.name )


@cinp.model( not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE', 'CALL' ] )
class NetworkInterface( models.Model ):
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )
  name = models.CharField( max_length=20 )
  is_provisioning = models.BooleanField( default=False )

  @property
  def subclass( self ):
    try:
      return self.realnetworkinterface
    except AttributeError:
      pass

    try:
      return self.abstractnetworkinterface
    except AttributeError:
      pass

    try:
      return self.abstractnetworkinterface
    except AttributeError:
      pass

    return self

  @property
  def type( self ):
    return 'Unknown'  # This class should not be used directly

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if verb == 'DESCRIBE':
      return True

    return False

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = '"{0}" is invalid'.format( self.name[ 0:50 ] )

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'NetworkInterface "{0}"'.format( self.physical_name )


@cinp.model( )
class RealNetworkInterface( NetworkInterface ):
  mac = models.CharField( max_length=18, unique=True, blank=True, null=True )
  pxe = models.ForeignKey( PXE, related_name='+', blank=True, null=True )

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'Real'

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not self.mac:
      self.mac = None

    else:
      if re.match( '([0-9a-f]{4}.){2}[0-9a-f]{4}', self.mac ):
        self.mac = self.mac.replace( '.', '' )

      if re.match( '[0-9a-f]{12}', self.mac ):  # this is #2, it will catch the stripped cisco notation, and the  : less notation
        self.mac = ':'.join( [ self.mac[ i: i + 2 ] for i in range( 0, 12, 2 ) ] )

      if not re.match( '([0-9a-f]{2}:){5}[0-9a-f]{2}', self.mac ):
        errors[ 'mac' ] = '"{0}" is invalid'.format( self.mac[ 0:50 ] )

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'RealNetworkInterface "{0}" mac "{1}"'.format( self.name, self.mac )


@cinp.model( )
class AbstractNetworkInterface( NetworkInterface ):

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'Abstract'

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'AbstractNetworkInterface "{0}"'.format( self.name )


@cinp.model( )
class AggragatedNetworkInterface( AbstractNetworkInterface ):
  master_interface = models.ForeignKey( NetworkInterface, related_name='+' )
  slaves = models.ManyToManyField( NetworkInterface, related_name='+' )
  paramaters = MapField()

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'Aggragated'

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'AggragatedNetworkInterface "{0}"'.format( self.name )


@cinp.model( property_list=( 'gateway', 'netmask', 'size', 'isIpV4' ) )
class AddressBlock( models.Model ):
  site = models.ForeignKey( Site, on_delete=models.CASCADE )
  subnet = IpAddressField()
  prefix = models.IntegerField()
  gateway_offset = models.IntegerField( blank=True, null=True )
  _max_address = IpAddressField( editable=False )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def gateway( self ):
    if self.gateway_offset is None:
      return None

    return IpToStr( StrToIp( self.subnet ) + self.gateway_offset )

  @property
  def netmask( self ):
    return IpToStr( CIDRNetmask( self.prefix, not self.isIpV4 ) )

  @property
  def size( self ):
    return CIDRNetworkSize( StrToIp( self.subnet ), self.prefix, not self.isIpV4 )

  @property
  def offsetBounds( self ):
    return CIDRNetworkBounds( StrToIp( self.subnet ), self.prefix, include_unusable=False, as_offsets=True )

  @property
  def isIpV4( self ):
    return IpIsV4( StrToIp( self.subnet ) )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return AddressBlock.objects.filter( site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    try:
      subnet_ip = StrToIp( self.subnet )
      ipv4 = IpIsV4( subnet_ip )
    except ValueError:
      ipv4 = None
      errors[ 'subnet' ] = 'Invalid Ip Address'

    if self.prefix is None or self.prefix < 1:
      errors[ 'prefix' ] = 'Min Prefix is 1'

    if errors:  # no point in continuing
      raise ValidationError( errors )

    if ipv4 is not None:
      if ipv4:
        if self.prefix > 32:
          errors[ 'prefix' ] = 'Max Prefix for ipv4 is 32'
      else:
        if self.prefix > 128:
          errors[ 'prefix' ] = 'Max Prefix for ipv6 is 128'

      if self.gateway_offset is not None:
        ( low, high ) = CIDRNetworkBounds( subnet_ip, self.prefix, False, True )
        if low == high:
          errors[ 'gateway_offset' ] = 'Gateway not possible in single host subnet'

        if self.gateway_offset < low or self.gateway_offset > high:
          errors[ 'gateway_offset' ] = 'Must be greater than {0} and less than {1}'.format( low, high )

    if errors:  # no point in continuing
      raise ValidationError( errors )

    ( subnet_ip, last_ip ) = CIDRNetworkBounds( subnet_ip, self.prefix, True )
    self.subnet = IpToStr( subnet_ip )
    self._max_address = IpToStr( last_ip )
    block_count = AddressBlock.objects.filter( subnet__gte=self.subnet, _max_address__lte=self.subnet ).count()
    block_count += AddressBlock.objects.filter( subnet__gte=self._max_address, _max_address__lte=self._max_address ).count()
    block_count += AddressBlock.objects.filter( _max_address__gte=self.subnet, _max_address__lte=self._max_address ).count()
    block_count += AddressBlock.objects.filter( subnet__gte=self.subnet, subnet__lte=self._max_address ).count()
    if block_count > 0:
      errors[ 'subnet' ] = 'This subnet/prefix overlaps with an existing Address Block'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'AddressBlock site "{0}" subnet "{1}/{2}"'.format( self.site, self.subnet, self.prefix )


@cinp.model( not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE' ], property_list=( 'ip_address', 'subclass', 'type', 'network', 'netmask', 'gateway', 'prefix' ) )
class BaseAddress( models.Model ):
  address_block = models.ForeignKey( AddressBlock, blank=True, null=True )
  offset = models.IntegerField( blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def ip_address( self ):
    if self.address_block is None or self.offset is None:
      return None

    return IpToStr( StrToIp( self.address_block.subnet ) + self.offset )

  @property
  def network( self ):
    if self.address_block is None:
      return None

    return self.address_block.subnet

  @property
  def netmask( self ):
    if self.address_block is None:
      return None

    return self.address_block.netmask

  @property
  def prefix( self ):
    if self.address_block is None:
      return None

    return self.address_block.prefix

  @property
  def gateway( self ):
    if self.address_block is None:
      return None

    return self.address_block.gateway

  @property
  def subclass( self ):
    try:
      return self.address
    except AttributeError:
      pass

    try:
      return self.reservedaddress
    except AttributeError:
      pass

    try:
      return self.dynamicaddress
    except AttributeError:
      pass

    return self

  @property
  def type( self ):
    real = self.subclass
    if real.__class__.__name__ == 'BaseAddress':
      return 'Unknown'

    return real.type

  @cinp.action( return_type={ 'type': 'Model', 'model': 'contractor.Utilities.models.BaseAddress' }, paramater_type_list=[ 'String' ] )
  @staticmethod
  def lookup( ip_address ):
    try:
      address_block = AddressBlock.objects.get( subnet__lte=ip_address, _max_address__gte=ip_address )
    except AddressBlock.DoesNotExist:
      return None

    offset = StrToIp( ip_address ) - StrToIp( address_block.subnet )
    try:
      return BaseAddress.objects.get( address_block=address_block, offset=offset )
    except BaseAddress.DoesNotExist:
      return None

    return None

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if verb == 'DESCRIBE':
      return True

    return False

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.offset is not None and self.address_block is None:
      errors[ 'offset' ] = 'Can not be specified without address_block'

    if self.address_block is not None and self.offset is None:
      errors[ 'address_block' ] = 'Can not be specified without offset'

    if self.address_block is not None and self.offset is not None:
      ( min_offset, max_offset ) = self.address_block.offsetBounds
      if self.offset is None or self.offset < min_offset or self.offset > max_offset:
        errors[ 'offset' ] = 'Must be greater than {0} and less than {1}'.format( min_offset, max_offset )

      if 'offest' not in errors and self.offset == self.address_block.gateway_offset:
        errors[ 'offset' ] = 'Conflicts with Gateway'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'address_block', 'offset' ), )

  def __str__( self ):
    return 'BaseAddress block "{0}" offset "{1}"'.format( self.address_block, self.offset )


@cinp.model( property_list=( 'ip_address', 'type', 'network', 'netmask', 'gateway', 'prefix' ) )
class Address( BaseAddress ):
  networked = models.ForeignKey( Networked )
  interface_name = models.CharField( max_length=20 )
  sub_interface = models.IntegerField( default=None, blank=True, null=True )
  vlan = models.IntegerField( default=0 )  # vlan = 0: Untagged/Native VLAN     vlan = 4096: Trunked
  pointer = models.ForeignKey( 'self', blank=True, null=True )
  is_primary = models.BooleanField( default=False )

  @property
  def ip_address( self ):
    if self.pointer is not None:
      return self.pointer.ip_address

    return super().ip_address

  @property
  def network( self ):
    if self.pointer is not None:
      return self.pointer.network

    return super().network

  @property
  def netmask( self ):
    if self.pointer is not None:
      return self.pointer.netmask

    return super().netmask

  @property
  def prefix( self ):
    if self.pointer is not None:
      return self.pointer.prefix

    return super().prefix

  @property
  def gateway( self ):
    if self.pointer is not None:
      return self.pointer.gateway

    return super().gateway

  @property
  def structure( self ):
    try:
      return self.networked.structure
    except ObjectDoesNotExist:
      return None

  @property
  def interface( self ):
    try:
      return self.networked.structure.foundation.interfaces.get( name=self.interface_name )
    except ObjectDoesNotExist:
      return None

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'Address'

  @cinp.list_filter( name='address_block', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Utilities.models.AddressBlock' } ] )
  @staticmethod
  def filter_address_block( address_block ):
    return Address.objects.filter( address_block=address_block )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.interface_name ):
      errors[ 'interface_name' ] = '"{0}" is invalid'.format( self.interface_name[ 0:50 ] )

    try:
      if self.address_block and self.networked and self.address_block.site != self.networked.site:
        errors[ 'address_block' ] = 'Address is not in the same site as the Networked it belongs to'
    except ObjectDoesNotExist:
      pass  # something else should make sure address_block and networked are defined

    if errors:  # if either of the above happen, don't bother with the rest
      raise ValidationError( errors )

    try:
      if self.pointer is not None:
        if self.address_block is not None:
          errors[ 'address_block' ] = 'Conflicts with Pointer'
          errors[ 'pointer' ] = 'Conflicts with Address_block'
        if self.offset is not None:
          errors[ 'offset' ] = 'Conflicts with Pointer'
          errors[ 'pointer' ] = 'Conflicts with Offset'
    except ObjectDoesNotExist:
      pass

    if not self.sub_interface:
      self.sub_interface = None
    else:
      if self.sub_interface < 0:
        errors[ 'sub_interface' ] = 'Must be a positive value'

    if self.vlan > 4096 or self.vlan < 0:
      errors[ 'vlan' ] = 'must be between 0 and 4096'

    if self.is_primary:
      if self.networked.address_set.filter( is_primary=True ).count() > 0:
        errors[ 'is_primary' ] = 'Networked allready has a primary ip'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Address in Block "{0}" offset "{1}" networked "{2}" on interface "{3}"'.format( self.address_block, self.offset, self.networked, self.interface_name )


@cinp.model( property_list=( 'ip_address', 'type' ) )
class ReservedAddress( BaseAddress ):
  reason = models.CharField( max_length=50 )

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'ReservedAddress'

  @cinp.list_filter( name='address_block', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Utilities.models.AddressBlock' } ] )
  @staticmethod
  def filter_address_block( address_block ):
    return ReservedAddress.objects.filter( address_block=address_block )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not self.address_block:
      errors[ 'address_block' ] = 'This field cannot be blank.'

    if not self.offset:
      errors[ 'offset' ] = 'This field cannot be blank.'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'ReservedAddress block "{0}" offset "{1}"'.format( self.address_block, self.offset )


@cinp.model( property_list=( 'ip_address', 'type', 'network', 'netmask', 'gateway', 'prefix' ) )
class DynamicAddress( BaseAddress ):  # no dynamic pools, thoes will be auto detected
  pxe = models.ForeignKey( PXE, related_name='+', blank=True, null=True )

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'DynamicAddress'

  @cinp.list_filter( name='address_block', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Utilities.models.AddressBlock' } ] )
  @staticmethod
  def filter_address_block( address_block ):
    return DynamicAddress.objects.filter( address_block=address_block )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not self.address_block:
      errors[ 'address_block' ] = 'This field cannot be blank.'

    if not self.offset:
      errors[ 'offset' ] = 'This field cannot be blank.'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'DynamicAddress block "{0}" offset "{1}"'.format( self.address_block, self.offset )


# and Powered
# class PowerPort( models.Model ):
#   other_end = models.ForeignKey( 'self' ) # or should there be a sperate table with the plug relation ships
#   updated = models.DateTimeField( editable=False, auto_now=True )
#   created = models.DateTimeField( editable=False, auto_now_add=True )
#   # powered by Structure
#   # provides power to foundation
