import re
import random

from django.db import models
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, IpAddressField, hostname_regex, name_regex
from contractor.BluePrint.models import PXE
from contractor.Site.models import Site
from contractor.lib.ip import IpIsV4, CIDRNetworkBounds, StrToIp, IpToStr, CIDRNetworkSize, CIDRNetmask, CIDRNetworkRange

cinp = CInP( 'Utilities', '0.1' )

network_name_regex = re.compile( r'^[a-zA-Z0-9][a-zA-Z0-9_\-]*(\.[0-9]{1,4})?$' )  # the ".[0-9]" is for networks that are vlans of other networks, some things like proxmox treat these as un-named special networks


class UtilitiesException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'exception': 'UtilitiesException', 'error': self.code, 'message': self.message }

  def __str__( self ):
    return 'UtilitiesException ({0}): {1}'.format( self.code, self.message )


def ipAddress2Native( ip_address ):
  try:
    address_block = AddressBlock.objects.get( subnet__lte=ip_address, _max_address__gte=ip_address )
  except AddressBlock.DoesNotExist:
    raise UtilitiesException( 'ADDRESS_NOT_FOUND', 'ip_address "{0}" does not exist in any existing Address Blocks'.format( ip_address ) )

  return address_block, StrToIp( ip_address ) - StrToIp( address_block.subnet )


@cinp.model()
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
  def primary_interface( self ):
    try:
      address = self.address_set.get( is_primary=True )
      return address.interface
    except ObjectDoesNotExist:
      return None

  @property
  def primary_address( self ):
    try:
      return self.address_set.get( is_primary=True )
    except Address.DoesNotExist:
      return None

  @property
  def provisioning_interface( self ):
    try:
      return self.structure.foundation.networkinterface_set.get( is_provisioning=True )
    except ObjectDoesNotExist:
      return None

  @property
  def provisioning_address( self ):
    provisioning_interface = self.provisioning_interface
    if provisioning_interface is None:
      return None

    interface_name = provisioning_interface.name
    if interface_name is None:
      return None

    try:
      return self.address_set.get( interface_name=interface_name, is_primary=True )
    except Address.DoesNotExist:
      try:
        return self.address_set.filter( interface_name=interface_name ).order_by( 'alias_index' )[ 0 ]
      except IndexError:
        pass
      return None

  @property
  def domain_name( self ):
    try:
      zone = self.site.zone
      if zone is None:
        return None

    except ( ObjectDoesNotExist, AttributeError ):
      return None

    return zone.fqdn

  @property
  def fqdn( self ):
    try:
      zone = self.site.zone
      if zone is None:
        return self.hostname

    except ( ObjectDoesNotExist, AttributeError ):
      return self.hostname

    return '{0}.{1}'.format( self.hostname, zone.fqdn )

  def getAddressList( self, interface ):
    result = []

    for address in self.address_set.filter( interface_name=interface.name ).order_by( 'alias_index' ):
      address_config = address.as_dict
      try:
        nab = NetworkAddressBlock.objects.get( network=interface.network, address_block=address.address_block )
        if nab.vlan is not None:
          address_config[ 'vlan' ] = nab.vlan
      except NetworkAddressBlock.DoesNotExist:
        pass

      result.append( address_config )

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, Networked )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not hostname_regex.match( self.hostname ):
      errors[ 'hostname' ] = 'invalid'

    try:
      zone = self.site.zone
    except ( ObjectDoesNotExist, AttributeError ):
      zone = None

    if zone is not None and zone.site_set.filter( networked__hostname=self.hostname ).exclude( networked__pk=self.pk ).count():
      errors[ 'hostname' ] = 'Hostname "{0}" allready used in DNS Zone "{1}"'.format( self.hostname, zone.pk )

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'site', 'hostname' ), )
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'Networked hostname "{0}" in "{1}"'.format( self.hostname, self.site.name )


@cinp.model( property_list=( 'gateway', 'netmask', 'size', 'isIpV4' ) )
class AddressBlock( models.Model ):
  name = models.CharField( max_length=40 )
  site = models.ForeignKey( Site, on_delete=models.PROTECT )
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

  @cinp.action( return_type={ 'type': 'Model', 'model': 'contractor.Utilities.models.Address' }, paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Utilities.models.Networked' }, { 'type': 'String' }, { 'type': 'Boolean' } ] )
  def nextAddress( self, networked, interface_name, is_primary ):  # TODO: wrap this in a transaction, or some other way to unwrap everything if it fails
    address = Address( networked=networked, interface_name=interface_name, is_primary=is_primary )
    if networked.structure.foundation.subclass.__class__.__name__ == 'DockerFoundation':
      # address.pointer = Address.objects.get( networked=structure.foundation.docker_host.members[0], interface_name='eth0' )
      return None  # set map_ports will do the address

    else:  # TODO: either retry till all_offsets is empty, or lock the Address table(s)
      all_offsets = set( CIDRNetworkRange( StrToIp( self.subnet ), self.prefix, False, True ) )
      if self.gateway_offset is not None:
        all_offsets = all_offsets - set( [ self.gateway_offset ] )

      if not all_offsets:
        raise UtilitiesException( 'NO_OFFSETS', 'No Available Offsets' )

      used_offsets = set( BaseAddress.objects.filter( address_block=self, offset__isnull=False ).values_list( 'offset', flat=True ) )
      address.address_block = self
      address.offset = random.choice( list( all_offsets - used_offsets ) )

    address.full_clean()
    address.save()

    return address

  @cinp.action( return_type='Map' )
  def usage( self ):
    result = {}
    result[ 'total' ] = self.size
    result[ 'static' ] = Address.objects.filter( address_block=self ).count()
    result[ 'reserved' ] = ReservedAddress.objects.filter( address_block=self ).count()
    result[ 'dynamic' ] = DynamicAddress.objects.filter( address_block=self ).count()
    if self.gateway_offset:
      result[ 'reserved' ] += 1

    return result

  @cinp.action( return_type={ 'type': 'Model', 'model': 'contractor.Utilities.models.AddressBlock' }, paramater_type_list=[ { 'type': 'Model', 'model': Site }, 'String' ] )
  @staticmethod
  def getWithNameSite( site, name ):
    try:
      return AddressBlock.objects.get( site=site, name=name )
    except AddressBlock.DoesNotExist:
      return None

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def filter_site( site ):
    return AddressBlock.objects.filter( site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if not cinp.basic_auth_check( user, verb, AddressBlock ):
      return False

    if verb == 'CALL':
      if action == 'usage':
        return True

      if action == 'nextAddress':
        return user.has_perm( 'Utilities.add_address' )

      return False

    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'invalid'

    try:
      subnet_ip = StrToIp( self.subnet )
    except ValueError:
      errors[ 'subnet' ] = 'Invalid Ip Address'

    if self.prefix is None or self.prefix < 1:
      errors[ 'prefix' ] = 'Min Prefix is 1'

    if errors:  # no point in continuing
      raise ValidationError( errors )

    if IpIsV4( subnet_ip ):
      if self.prefix > 32:
        errors[ 'prefix' ] = 'Max Prefix for ipv4 is 32'
    else:
      if self.prefix > 128:
        errors[ 'prefix' ] = 'Max Prefix for ipv6 is 128'

    if errors:  # no point in continuing
      raise ValidationError( errors )

    ( low_offset, high_offset ) = CIDRNetworkBounds( subnet_ip, self.prefix, False, True )
    ( subnet_ip, last_ip ) = CIDRNetworkBounds( subnet_ip, self.prefix, True )

    self.subnet = IpToStr( subnet_ip )
    self._max_address = IpToStr( last_ip )

    if self.pk is not None:
      ABobjects = AddressBlock.objects.filter( ~Q( pk=self.pk ), site=self.site )
    else:
      ABobjects = AddressBlock.objects.filter( site=self.site )
    block_count = ABobjects.filter( subnet__gte=self.subnet, _max_address__lte=self.subnet ).count()
    block_count += ABobjects.filter( subnet__gte=self._max_address, _max_address__lte=self._max_address ).count()
    block_count += ABobjects.filter( _max_address__gte=self.subnet, _max_address__lte=self._max_address ).count()
    block_count += ABobjects.filter( subnet__gte=self.subnet, subnet__lte=self._max_address ).count()
    if block_count > 0:
      errors[ 'subnet' ] = 'This subnet/prefix overlaps with an existing Address Block in the same site'

    if errors:  # no point in continuing
      raise ValidationError( errors )

    if self.gateway_offset is not None:
      if low_offset == high_offset:
        errors[ 'gateway_offset' ] = 'Gateway not possible in single host subnet'

      if self.gateway_offset < low_offset or self.gateway_offset > high_offset:
        errors[ 'gateway_offset' ] = 'Must be greater than {0} and less than {1}'.format( low_offset, high_offset )

    offset_list = self.baseaddress_set.all().values_list( 'offset', flat=True )
    if sum( [ i > high_offset for i in offset_list ] ) > 0:
      errors[ 'prefix' ] = 'Prefix excludes existing addresses'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'site', 'name' ), )
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'AddressBlock "{0}" in "{1}" subnet "{2}/{3}"'.format( self.name, self.site, self.subnet, self.prefix )


@cinp.model()
class Network( models.Model ):
  name = models.CharField( max_length=40 )
  site = models.ForeignKey( Site, on_delete=models.PROTECT )
  mtu = models.IntegerField( blank=True, null=True )
  address_block_list = models.ManyToManyField( AddressBlock, through='NetworkAddressBlock' )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.action( return_type={ 'type': 'Model', 'model': 'contractor.Utilities.models.Network' }, paramater_type_list=[ { 'type': 'Model', 'model': Site }, 'String' ] )
  @staticmethod
  def getWithNameSite( site, name ):
    try:
      return Network.objects.get( site=site, name=name )
    except Network.DoesNotExist:
      return None

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def filter_site( site ):
    return Network.objects.filter( site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, Network )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not network_name_regex.match( self.name ):
      errors[ 'name' ] = 'invalid'

    if self.mtu is not None and ( self.mtu > 9022 or self.mtu < 512 ):
      errors[ 'mtu' ] = 'must be between 512 and 9022'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'site', 'name' ), )
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'Network "{0}" in "{1}"'.format( self.name, self.site )


@cinp.model()
class NetworkAddressBlock( models.Model ):
  network = models.ForeignKey( Network, on_delete=models.CASCADE )
  address_block = models.ForeignKey( AddressBlock, on_delete=models.CASCADE )
  vlan = models.IntegerField( blank=True, null=True )  # 0: Untagged/Native VLAN, 4095: Trunked, None/null == 0
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.list_filter( name='network', paramater_type_list=[ { 'type': 'Model', 'model': Network } ] )
  @staticmethod
  def filter_network( network ):
    return NetworkAddressBlock.objects.filter( network=network )

  @cinp.list_filter( name='address_block', paramater_type_list=[ { 'type': 'Model', 'model': AddressBlock } ] )
  @staticmethod
  def filter_address_block( address_block ):
    return NetworkAddressBlock.objects.filter( address_block=address_block )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, NetworkAddressBlock )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not self.vlan:
      self.vlan = None
    elif self.vlan > 4095 or self.vlan < 0:
      errors[ 'vlan' ] = 'must be between 0 and 4095'

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'NetworkAddressBlock "{0}" to "{1}"'.format( self.network, self.address_block )


@cinp.model( not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE', 'CALL' ], property_list=( 'type', ) )
class NetworkInterface( models.Model ):
  name = models.CharField( max_length=20 )
  network = models.ForeignKey( Network, on_delete=models.PROTECT )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def subclass( self ):
    try:
      return self.realnetworkinterface
    except AttributeError:
      pass

    try:
      return self.aggregatednetworkinterface  # must come before abstract b/c aggregated is abstract
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

  @property
  def config( self ):
    result = { 'name': self.name, 'network': self.network.name }
    if self.network.mtu is not None:
      result[ 'mtu' ] = self.network.mtu

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, NetworkInterface )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.name and not name_regex.match( self.name ):
      errors[ 'name' ] = 'invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    default_permissions = ()  # nothing

  def __str__( self ):
    return 'NetworkInterface "{0}"'.format( self.name )


@cinp.model( property_list=( 'type', ) )
class RealNetworkInterface( NetworkInterface ):
  mac = models.CharField( max_length=18, blank=True, null=True )  # in a globally unique world we would set this to unique, but these virtual days we have to many ways to use the same mac safely, so good luck.
  foundation = models.ForeignKey( 'Building.Foundation', related_name='networkinterface_set', on_delete=models.CASCADE )
  is_provisioning = models.BooleanField( default=False )
  physical_location = models.CharField( max_length=100 )
  link_name = models.CharField( max_length=100, blank=True, null=True )  # Until NetworkInterfaces can plug to each other and better ways of storing LLDP info
  pxe = models.ForeignKey( PXE, related_name='+', blank=True, null=True, on_delete=models.PROTECT )

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'Real'

  @property
  def config( self ):
    result = super().config
    result[ 'mac' ] = self.mac
    result[ 'physical_location' ] = self.physical_location
    result[ 'link_name' ] = self.link_name

    return result

  @cinp.list_filter( name='foundation', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Foundation' } ] )
  @staticmethod
  def filter_foundation( foundation ):
    return RealNetworkInterface.objects.filter( foundation=foundation )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, RealNetworkInterface )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.physical_location ):
      errors[ 'physical_location' ] = 'invalid'

    if self.is_provisioning:
      if self.pk is not None:
        RNIobjects = self.foundation.networkinterface_set.filter( ~Q( pk=self.pk ), is_provisioning=True )
      else:
        RNIobjects = self.foundation.networkinterface_set.filter( is_provisioning=True )

      if RNIobjects.count() > 0:
        errors[ 'is_provisioning' ] = 'This foundation allready has a provisioning interface'

    if not self.mac:
      self.mac = None

    else:
      self.mac = self.mac.lower()

      if re.match( '([0-9a-f]{4}.){2}[0-9a-f]{4}', self.mac ):
        self.mac = self.mac.replace( '.', '' )

      if re.match( '[0-9a-f]{12}', self.mac ):  # this is #2, it will catch the stripped cisco notation, and the : less notation
        self.mac = ':'.join( [ self.mac[ i: i + 2 ] for i in range( 0, 12, 2 ) ] )

      if not re.match( '([0-9a-f]{2}:){5}[0-9a-f]{2}', self.mac ):
        errors[ 'mac' ] = '"{0}" is invalid'.format( self.mac[ 0:50 ] )

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'foundation', 'physical_location' ), )
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'RealNetworkInterface "{0}" mac "{1}"'.format( self.name, self.mac )


@cinp.model( property_list=( 'type', ) )
class AbstractNetworkInterface( NetworkInterface ):
  structure = models.ForeignKey( 'Building.Structure', related_name='networkinterface_set', on_delete=models.CASCADE )

  @property
  def subclass( self ):
    try:
      return self.aggregatednetworkinterface
    except AttributeError:
      pass

    return self

  @property
  def type( self ):
    return 'Abstract'

  @property
  def mac( self ):
    return None

  @cinp.list_filter( name='structure', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Structure' } ] )
  @staticmethod
  def filter_structure( structure ):
    return AbstractNetworkInterface.objects.filter( structure=structure )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, AbstractNetworkInterface )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.structure_id:
      try:
        if self.pk is not None:
          AbstractNetworkInterface.objects.filter( ~Q( pk=self.pk ) ).get( name=self.name, structure=self.structure )
        else:
          AbstractNetworkInterface.objects.get( name=self.name, structure=self.structure )

        errors[ 'structure' ] = 'interface name "{0}" allready in use for structure'.format( self.name )
      except AbstractNetworkInterface.DoesNotExist:
        pass

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # unique_together = ( ( 'structure', 'name' ), )  would like to do this, but 'name' isn't "local" to this model, so we are doing it ourselves
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'AbstractNetworkInterface "{0}"'.format( self.name )


@cinp.model( property_list=( 'type', ) )
class AggregatedNetworkInterface( AbstractNetworkInterface ):
  primary_interface = models.ForeignKey( NetworkInterface, related_name='+', on_delete=models.CASCADE )
  secondary_interfaces = models.ManyToManyField( NetworkInterface, related_name='+' )
  paramaters = MapField( blank=True, null=True )

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'Aggregated'

  @property
  def mac( self ):
    return self.primary_interface.subclass.mac

  @property
  def config( self ):
    result = super().config
    result[ 'primary' ] = self.primary_interface.name  # name b/c this is inside the OS
    result[ 'secondary' ] = [ i.name for i in self.secondary_interfaces.all() ]
    result[ 'paramaters' ] = self.paramaters

    return result

  @cinp.list_filter( name='structure', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Structure' } ] )
  @staticmethod
  def filter_structure( structure ):
    return AggregatedNetworkInterface.objects.filter( structure=structure )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, AggregatedNetworkInterface )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    try:
      foundation = self.primary_interface.foundation
    except AttributeError:
      foundation = None

    try:
      structure = self.primary_interface.structure
    except AttributeError:
      structure = None

    if foundation is not None and self.structure.foundation != foundation:
        errors[ 'primary_interface' ] = 'must belong to the same foundation/structure as this interface'

    if structure is not None and self.structure != structure:
      errors[ 'primary_interface' ] = 'must belong to the same foundation/structure as this interface'

    if self.pk is not None:
      if self.primary_interface.pk in self.secondary_interfaces.all().values_list( 'pk', flat=True ):
        errors[ 'primary_interface' ] = 'primary can not be one of the secondaries'

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'AggregatedNetworkInterface "{0}"'.format( self.name )


def aggregated_secondary_changed( sender, instance, action, pk_set, **kwards ):
  if action != 'pre_add':
    return

  errors = {}

  iface_list = NetworkInterface.objects.filter( pk__in=pk_set )

  for iface in iface_list:
    iface = iface.subclass
    try:
      foundation = iface.foundation
    except AttributeError:
      foundation = None

    try:
      structure = iface.structure
    except AttributeError:
      structure = None

    if foundation is not None and instance.structure.foundation != foundation:
      errors[ 'secondary_interfaces' ] = 'must belong to the same foundation/structure as this interface'

    if structure is not None and instance.structure != structure:
      errors[ 'secondary_interfaces' ] = 'must belong to the same foundation/structure as this interface'

    if instance.primary_interface.network != iface.network:
      errors[ 'secondary_interfaces' ] = 'must belong to the same network as the primary_interface'

  if instance.primary_interface.pk in pk_set:
    errors[ 'primary_interface' ] = 'primary can not be one of the secondaries'

  if errors:
    raise ValidationError( errors )


m2m_changed.connect( aggregated_secondary_changed, sender=AggregatedNetworkInterface.secondary_interfaces.through )


@cinp.model( not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE' ], property_list=( 'type', 'ip_address', 'subnet', 'netmask', 'prefix', 'gateway' ) )
class BaseAddress( models.Model ):
  address_block = models.ForeignKey( AddressBlock, blank=True, null=True, on_delete=models.CASCADE )
  offset = models.IntegerField( blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def console( self ):
    return 'console'

  @property
  def ip_address( self ):
    if self.address_block is None or self.offset is None:
      return None

    return IpToStr( StrToIp( self.address_block.subnet ) + self.offset )

  @property
  def subnet( self ):
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
  def as_dict( self ):
    return {
             'address': self.ip_address,  # set to 'dhcp' for dhcp
             'netmask': self.netmask,
             'prefix': self.prefix,
             'subnet': self.subnet,
             'gateway': self.gateway,
             'auto': True
           }

  @property
  def interface( self ):
      return None

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

  @cinp.action( return_type={ 'type': 'Model', 'model': 'contractor.Utilities.models.BaseAddress' }, paramater_type_list=[ 'String', { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def lookup( ip_address, site=None ):
    try:
      ip_address_ip = StrToIp( ip_address )
    except ValueError:
      return None

    located_list = []
    ip_address = IpToStr( ip_address_ip )  # so it is in a consistant format
    if site is not None:
      query_set = AddressBlock.objects.filter( site=site )
    else:
      query_set = AddressBlock.objects.all()

    for address_block in query_set.filter( subnet__lte=ip_address, _max_address__gte=ip_address ):
      offset = ip_address_ip - StrToIp( address_block.subnet )
      try:
        located_list.append( BaseAddress.objects.get( address_block=address_block, offset=offset ) )
      except BaseAddress.DoesNotExist:
        pass

    if len( located_list ) == 1:
      return located_list[0]

    return None

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if not cinp.basic_auth_check( user, verb, BaseAddress ):
      return False

    if verb == 'CALL':
      return action == 'lookup'

    return True

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
    default_permissions = ()

  def __str__( self ):
    return 'BaseAddress block "{0}" offset "{1}"'.format( self.address_block, self.offset )


@cinp.model( property_list=( 'type', 'ip_address', 'subnet', 'netmask', 'prefix', 'gateway' ) )
class Address( BaseAddress ):
  networked = models.ForeignKey( Networked, on_delete=models.CASCADE )
  interface_name = models.CharField( max_length=20 )
  alias_index = models.IntegerField( default=None, blank=True, null=True )  # use None for one/first ip on that interface, leave blank, NOTE: gateway/is_primary/dhcp is taken from index "None"
  pointer = models.ForeignKey( 'self', blank=True, null=True, on_delete=models.PROTECT )
  is_primary = models.BooleanField( default=False )

  @staticmethod
  def fromIPAddress( site, ip_address ):
    try:
      ip_address_ip = StrToIp( ip_address )
    except ValueError:
      return None

    ip_address = IpToStr( ip_address_ip )  # so it is in a consistant format
    try:
      address_block = AddressBlock.objects.get( site=site, subnet__lte=ip_address, _max_address__gte=ip_address )
    except AddressBlock.DoesNotExist:
      return None

    offset = ip_address_ip - StrToIp( address_block.subnet )

    return Address( address_block=address_block, offset=offset )

  @property
  def console( self ):
    foundation = None
    try:
      foundation = self.networked.structure.foundation
    except ( ObjectDoesNotExist, AttributeError ):
      pass

    if foundation is not None:
      return foundation.subclass.console

    return 'console'

  @property
  def ip_address( self ):
    if self.pointer is not None:
      return self.pointer.ip_address

    return super().ip_address

  @property
  def subnet( self ):
    if self.pointer is not None:
      return self.pointer.subnet

    return super().subnet

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
  def as_dict( self ):
    result = super().as_dict
    result[ 'alias_index' ] = self.alias_index
    result[ 'primary' ] = self.is_primary
    return result

  @property
  def interface( self ):
    try:
      return self.networked.structure.foundation.networkinterface_set.get( name=self.interface_name )
    except ObjectDoesNotExist:
      pass

    try:
      return self.networked.structure.networkinterface_set.get( name=self.interface_name ).subclass
    except ObjectDoesNotExist:
      pass

    return None

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'Address'

  @cinp.list_filter( name='address_block', paramater_type_list=[ { 'type': 'Model', 'model': AddressBlock } ] )
  @staticmethod
  def filter_address_block( address_block ):
    return Address.objects.filter( address_block=address_block )

  @cinp.list_filter( name='structure', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Structure' } ] )
  @staticmethod
  def filter_structure( structure ):
    return Address.objects.filter( networked=structure )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, Address )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.interface_name ):
      errors[ 'interface_name' ] = 'invalid'

    try:  # TODO: Do we realy care about this.... I think the only think that might care is the DNS, the host CNAME and all
      if self.is_primary and self.address_block and self.networked and self.address_block.site != self.networked.site:
        errors[ 'address_block' ] = 'Primary Address is not in the same site as the Networked it belongs to'
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

    if not self.alias_index:
      self.alias_index = None
    else:
      if self.alias_index < 1:
        errors[ 'alias_index' ] = 'If Defined, must be greater than 1'

    if self.is_primary:
      if self.pk is not None:
        Aobjects = self.networked.address_set.filter( ~Q( pk=self.pk ) )
      else:
        Aobjects = self.networked.address_set.all()

      if Aobjects.filter( is_primary=True ).count() > 0:
        errors[ 'is_primary' ] = 'Networked allready has a primary ip'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'interface_name', 'alias_index' ), )
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'Address in Block "{0}" offset "{1}" networked "{2}" on interface "{3}"'.format( self.address_block, self.offset, self.networked, self.interface_name )


@cinp.model( property_list=( 'type', 'ip_address', 'subnet', 'netmask', 'prefix', 'gateway' ) )
class ReservedAddress( BaseAddress ):
  reason = models.CharField( max_length=50 )

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'ReservedAddress'

  @cinp.list_filter( name='address_block', paramater_type_list=[ { 'type': 'Model', 'model': AddressBlock } ] )
  @staticmethod
  def filter_address_block( address_block ):
    return ReservedAddress.objects.filter( address_block=address_block )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, ReservedAddress )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not self.address_block:
      errors[ 'address_block' ] = 'This field cannot be blank.'

    if not self.offset:
      errors[ 'offset' ] = 'This field cannot be blank.'

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'ReservedAddress block "{0}" offset "{1}"'.format( self.address_block, self.offset )


@cinp.model( property_list=( 'type', 'ip_address', 'subnet', 'netmask', 'prefix', 'gateway' ) )
class DynamicAddress( BaseAddress ):  # no dynamic pools, thoes will be auto detected
  pxe = models.ForeignKey( PXE, related_name='+', blank=True, null=True, on_delete=models.CASCADE )

  @property
  def subclass( self ):
    return self

  @property
  def type( self ):
    return 'DynamicAddress'

  @cinp.list_filter( name='address_block', paramater_type_list=[ { 'type': 'Model', 'model': AddressBlock } ] )
  @staticmethod
  def filter_address_block( address_block ):
    return DynamicAddress.objects.filter( address_block=address_block )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, DynamicAddress )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not self.address_block:
      errors[ 'address_block' ] = 'This field cannot be blank.'

    if not self.offset:
      errors[ 'offset' ] = 'This field cannot be blank.'

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'DynamicAddress block "{0}" offset "{1}"'.format( self.address_block, self.offset )


# and Powered
# class PowerPort( models.Model ):
#   other_end = models.ForeignKey( 'self' , on_delete=models.CASCADE ) # or should there be a sperate table with the plug relation ships
#   updated = models.DateTimeField( editable=False, auto_now=True )
#   created = models.DateTimeField( editable=False, auto_now_add=True )
#   # powered by Structure
#   # provides power to foundation
