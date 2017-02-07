from django.db import models
#from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, hostname_regex
from contractor.BluePrint.models import PXE
from contractor.Site.models import Site


cinp = CInP( 'Utilities', '0.1' )


@cinp.model( )
class Networked( models.Model ):
  hostname = models.CharField( max_length=100 )
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it

  class Meta:
    unique_together = ( ( 'site', 'hostname' ), )

  def clean( self, *args, **kwargs ): # verify hostname
    if not hostname_regex.match( self.hostname ):
      raise ValidationError( 'Structure hostname "{0}" is invalid'.format( self.name ) )

    super().clean( *args, **kwargs )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Networked "{0}"'.format( self.physical_name )


@cinp.model( not_allowed_method_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE', 'CALL' ] )
class NetworkInterface( models.Model ):
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def address_list( self ):
    return []

  @property
  def primary_address( self ):
    return 'address'

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    if method == 'DESCRIBE':
      return True

    return False

  def __str__( self ):
    return 'NetworkInterface "{0}"'.format( self.physical_name )


@cinp.model( )
class PhysicalNetworkInterface( NetworkInterface ):
  mac = models.CharField( max_length=18, primary_key=True )
  pxe = models.ForeignKey( PXE, related_name='+' )
  physical_name = models.CharField( max_length=20 )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'PhysicalNetworkInterface "{0}" mac "{1}"'.format( self.name, self.mac )


@cinp.model( )
class VirtualNetworkInterface( NetworkInterface ):
  logical_name = models.CharField( max_length=20 )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'VirtualNetworkInterface "{0}"'.format( self.name )


@cinp.model( )
class AggragatedNetworkInterface( VirtualNetworkInterface ):
  master_interface = models.ForeignKey( NetworkInterface, related_name='+' )
  slaves = models.ManyToManyField( NetworkInterface, related_name='+' )
  paramaters = MapField()

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'AggragatedNetworkInterface "{0}"'.format( self.name )


@cinp.model( )
class AddressBlock( models.Model ):
  cluster = models.ForeignKey( Site, on_delete=models.CASCADE )
  subnet = models.GenericIPAddressField( protocol='both', blank=True, null=True )
  prefix = models.IntegerField()
  gateway = models.GenericIPAddressField( protocol='both', blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def dns_servers( self ):
    return []
    # get config from cluster and return dns servers, if none return empty []

  @property
  def tftp_servers( self ):
    return []

  @property
  def syslog_servers( self ):
    return []

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'AddressBlock cluster "{0}" subnet "{1}/{2}"'.format( self.cluster, self.subnet, self.prefix )

@cinp.model( not_allowed_method_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE', 'CALL' ] )
class BaseAddress( models.Model ):
  block = models.ForeignKey( AddressBlock )
  offset = models.IntegerField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def address( self ):
    result = self.block.subnet
    result + self.offset
    if ipv4:
      return asipv4( result )
    else:
      return asipv6( result )

  class Meta:
    abstract = True

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    if method == 'DESCRIBE':
      return True

    return False

  def __str__( self ):
    return 'BaseAddress block "{0}" offset "{1}"'.format( self.block, self.offset )


@cinp.model( )
class Address( BaseAddress ):
  networked = models.ForeignKey( Networked )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Address block "{0}" offset "{1}" networked "{2}"'.format( self.block, self.offset, self.networked )

@cinp.model( )
class ReservedAddress( BaseAddress ):
  reason = models.CharField( max_length=50 )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'ReservedAddress block "{0}" offset "{1}"'.format( self.block, self.offset )


@cinp.model( )
class DynamicAddress( BaseAddress ): # no dynamic pools, thoes will be auto detected
  pass

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'DynamicAddress block "{0}" offset "{1}"'.format( self.block, self.offset )


# and Powered
# class PowerPort( models.Model ):
#   other_end = models.ForeignKey( 'self' ) # or should there be a sperate table with the plug relation ships
#   updated = models.DateTimeField( editable=False, auto_now=True )
#   created = models.DateTimeField( editable=False, auto_now_add=True )
#   # powered by Structure
#   # provides power to foundation
