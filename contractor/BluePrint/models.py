from django.db import models
from django.core.exceptions import ValidationError

from contractor.fields import JSONField, name_regex

# these are the templates, describe how soomething is made and the template of the thing it's made on

class BluePrint( models.Model ):
  name = models.CharField( max_length=20, primary_key=True )
  description = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  scripts = models.ManyToManyField( 'Script', through='BluePrintScript' )
  config_values = JSONField( blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def config( self ): # combine depth first the config values
    return {}

  @property
  def script_map( self ):
    result = {}

    for bps in self.blueprintscript_set.all():
      result[ bps.name ] = bps.script.script

    return result

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not name_regex.match( self.name ):
      raise ValidationError( 'BluePrint name "{0}" is invalid'.format( self.name ) )

  def __str__( self ):
    return 'BluePrint "{0}"({1})'.format( self.description, self.name )


# this has the template to define what to match to, weither it be a piece of hardware, a complex of some type
# this is then used to prepare that vm/blade/device in a non blueprint specific way
# the material is not associated with the sctructure until fully prepared
# ipmi type ip addresses will belong to the material, they belong to the device not the OS on the device anyway
# will need a working pool of "eth0" type ips for the prepare
class FoundationBluePrint( BluePrint ):
  template = JSONField()

  @property
  def subcontractor( self ): # ie the manager that is used to deal with this type of Material
    return { 'type': None }

  def __str__( self ):
    return 'FoundationBluePrint "{0}"({1})'.format( self.description, self.name )


class StructureBluePrint( BluePrint ):
  foundation_list = models.ManyToManyField( FoundationBluePrint ) # list of possible foundations this blueprint could be implemented on

  def __str__( self ):
    return 'StructureBluePrint "{0}"({1})'.format( self.description, self.name )


class Script( models.Model ):
  name = models.CharField( max_length=20, primary_key=True )
  description = models.CharField( max_length=200 )
  script = models.TextField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not name_regex.match( self.name ):
      raise ValidationError( 'BluePrint name "{0}" is invalid'.format( self.name ) )

  def __str__( self ):
    return 'Script "{0}"({1})'.format( self.description, self.name )


class BluePrintScript( models.Model ):
  blueprint = models.ForeignKey( BluePrint, on_delete=models.CASCADE )
  script = models.ForeignKey( Script, on_delete=models.CASCADE )
  name = models.CharField( max_length=50 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not name_regex.match( self.name ):
      raise ValidationError( 'BluePrint Script name "{0}" is invalid'.format( self.name ) )

  def __unicode__( self ):
    return 'BluePrintScript for BluePrint "{0}" Named "{1}" Script "{2}"' % ( self.blueprint, self.name, self.script )

  def __str__( self ):
    return 'BluePrintScript for blueprint "{0}" name "{1}"'.format( self.blueprint.name, self.name )

  class Meta:
    unique_together = ( ( 'blueprint', 'name' ), )
