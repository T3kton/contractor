from django.db import models
from django.core.exceptions import ValidationError

from contractor.fields import JSONField, name_regex

# this is the what we want implemented, ie where, how it's grouped and waht is in thoes sites/groups, the logical aspect

class Site( models.Model ):
  name = models.CharField( max_length=20, primary_key=True )
  description = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  config_values = JSONField( blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def config( self ): # combine depth first the config values
    return {}

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not name_regex.match( self.name ):
      raise ValidationError( 'Site name "{0}" is invalid'.format( self.name ) )

  def __str__( self ):
    return 'Site "{0}"({1})'.format( self.description, self.name )

#TODO: rename this namespace to Site
