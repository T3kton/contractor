from django.db import models
#from django.core.exceptions import ValidationError

from contractor.fields import JSONField, hostname_regex
from contractor.BluePrint.models import PXE
from contractor.Site.models import Site


class Networked( models.Model ):
  hostname = models.CharField( max_length=100 )
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it

  class Meta:
    unique_together = ( ( 'site', 'hostname' ), )

  def clean( self, *args, **kwargs ): # verify hostname
    if not hostname_regex.match( self.hostname ):
      raise ValidationError( 'Structure hostname "{0}" is invalid'.format( self.name ) )

    super().clean( *args, **kwargs )

  def __str__( self ):
    return 'Networked "{0}"'.format( self.physical_name )


class NetworkInterface( models.Model ):
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def address_list( self ):
    return []

  @property
  def primary_address( self ):
    return 'address'

  def __str__( self ):
    return 'NetworkInterface "{0}"'.format( self.physical_name )


class PhysicalNetworkInterface( NetworkInterface ):
  mac = models.CharField( max_length=18, primary_key=True )
  pxe = models.ForeignKey( PXE, related_name='+' )
  physical_name = models.CharField( max_length=20 )

  def __str__( self ):
    return 'PhysicalNetworkInterface "{0}" mac "{1}"'.format( self.name, self.mac )


class VirtualNetworkInterface( NetworkInterface ):
  logical_name = models.CharField( max_length=20 )

  def __str__( self ):
    return 'VirtualNetworkInterface "{0}"'.format( self.name )


class AggragatedNetworkInterface( VirtualNetworkInterface ):
  master_interface = models.ForeignKey( NetworkInterface, related_name='+' )
  slaves = models.ManyToManyField( NetworkInterface, related_name='+' )
  paramaters = JSONField()

  def __str__( self ):
    return 'AggragatedNetworkInterface "{0}"'.format( self.name )


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


class Address( BaseAddress ):
  networked = models.ForeignKey( Networked )


class ReservedAddress( BaseAddress ):
  reason = models.CharField( max_length=50 )


class DynamicAddress( BaseAddress ): # no dynamic pools, thoes will be auto detected
  pass


# and Powered
# class PowerPort( models.Model ):
#   other_end = models.ForeignKey( 'self' ) # or should there be a sperate table with the plug relation ships
#   updated = models.DateTimeField( editable=False, auto_now=True )
#   created = models.DateTimeField( editable=False, auto_now_add=True )
#   # powered by Structure
#   # provides power to foundation
