import re
from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

cinp = CInP( 'Directory', '0.1' )

zone_name_regex = re.compile( '^[a-z][a-z0-9]+$' )  # NOTE: do not allow '.', it can cause problems with sub zones, also these can be used for filename, so must be filesystem safe
entry_name_regex = re.compile( '^[a-z][a-z0-9]+$')  # NOTE: do not allow '.', it can cause problems with sub zones
absolute_name_regex = re.compile( '^([a-z][a-z0-9]+\.)+[a-z][a-z0-9]+\.$' )


@cinp.model( property_list=( 'fqdn' ) )
class Zone( models.Model ):
  name = models.CharField( max_length=100 )
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  ttl = models.IntegerField( default=3600 )
  refresh = models.IntegerField( default=86400 )
  retry = models.IntegerField( default=7200 )
  expire = models.IntegerField( default=36000 )
  minimum = models.IntegerField( default=172800 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def fqdn( self ):
    if self.parent is None:
      return self.name

    return self.name + '.' + self.parent.fqdn

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):  # TODO: also make sure there are no hostnames in the attached sites of the parent that have the same name as this, this logic needs to go on Networked as well
    super().clean( *args, **kwargs )
    errors = {}

    self.name = self.name.lower()

    if not zone_name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'name', 'parent' ), )

  def __str__( self ):
    return 'Zone "{0}"({1})'.format( self.name, self.fqdn )


@cinp.model()
class Entry( models.Model ):
  TYPE_CHOICES = ( 'MX', 'SRV', 'CNAME', 'TXT' )
  zone = models.ForeignKey( Zone, on_delete=models.CASCADE )
  type = models.CharField( max_length=20, choices=[ ( i, i ) for i in TYPE_CHOICES ] )
  name = models.CharField( max_length=255 )
  priority = models.IntegerField( blank=True, null=True )  # MX, SRV
  weight = models.IntegerField( blank=True, null=True )  # SRV
  port = models.IntegerField( blank=True, null=True )  # SRV
  target = models.CharField( max_length=255 )  # MX, SRV, CNAME, TXT
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not entry_name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if self.weight is not None and ( self.weight < 1 or self.weight > 4096 ):
      errors[ 'weight' ] = 'Invalid'

    if self.port is not None and ( self.port < 1 or self.port > 65535 ):
      errors[ 'port' ] = 'port'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Entry of type "{0}" for "{1}" in "{2}"'.format( self.type, self.name, self.zone )
