from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, name_regex, config_name_regex
from contractor.lib.config import getConfig

# this is the what we want implemented, ie where, how it's grouped and waht is in thoes sites/groups, the logical aspect

cinp = CInP( 'Site', '0.1' )


@cinp.model()
class Site( models.Model ):
  name = models.CharField( max_length=20, primary_key=True )
  description = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  config_values = MapField( blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'name "{0}" is invalid'.format( self.name )

    for name in self.config_values:
      if not config_name_regex.match( name ):
        errors[ 'config_values' ] = 'config item name "{0}" is invalid'.format( name )
        break

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Site "{0}"({1})'.format( self.description, self.name )
