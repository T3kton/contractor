from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, JSONField, StringListField, name_regex
from contractor.tscript import parser
from contractor.lib.config import getConfig

# these are the templates, describe how soomething is made and the template of the thing it's made on

cinp = CInP( 'BluePrint', '0.1' )


@cinp.model( not_allowed_method_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE', 'CALL' ] )
class BluePrint( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )
  description = models.CharField( max_length=200 )
  scripts = models.ManyToManyField( 'Script', through='BluePrintScript' )
  config_values = MapField( blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def get_script( self, name ):
    try:
      return self.blueprintscript_set.get( name=name ).script.script
    except BluePrintScript.DoesNotExist:
      if self.parent is not None:
        return self.parent.get_script( name )
      else:
        raise ValueError( 'BluePrint "{0}" does not have a script named "{1}"'.format( self.name, name ) )

  def getConfig( self ):
    return getConfig( self )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'BluePrint Script name "{0}" is invalid'.format( self.name )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    if method == 'DESCRIBE':
      return True

    return False

  def __str__( self ):
    return 'BluePrint "{0}"({1})'.format( self.description, self.name )


# this has the template to define what to match to, weither it be a piece of hardware, a complex of some type
# this is then used to prepare that vm/blade/device in a non blueprint specific way
# the material is not associated with the sctructure until fully prepared
# ipmi type ip addresses will belong to the material, they belong to the device not the OS on the device anyway
# will need a working pool of "eth0" type ips for the prepare
@cinp.model( property_list=( 'subcontractor', ) )
class FoundationBluePrint( BluePrint ):
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  foundation_type_list = StringListField( max_length=200 ) # list of the foundation types this blueprint can be used for
  template = JSONField( default={}, blank=True )
  physical_interface_names = StringListField( max_length=200 )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @property
  def subcontractor( self ):
    return { 'type': None }

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not isinstance( self.template, dict ):
      errors[ 'template' ] = 'template must be a dict'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'FoundationBluePrint "{0}"({1})'.format( self.description, self.name )


@cinp.model(  )
class StructureBluePrint( BluePrint ):
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  foundation_blueprint_list = models.ManyToManyField( FoundationBluePrint ) # list of possible foundations this blueprint could be implemented on

  @property
  def combined_foundation_blueprint_list( self ):
    result = list( self.foundation_blueprint_list.all() )
    if self.parent is not None:
      result += self.parent.combined_foundation_blueprint_list

    return list( set( result ) )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'StructureBluePrint "{0}"({1})'.format( self.description, self.name )


@cinp.model()
class Script( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )
  description = models.CharField( max_length=200 )
  script = models.TextField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'BluePrint name "{0}" is invalid'.format( self.name )

    results = parser.lint( self.script )
    if results is not None:
      errors[ 'script' ] = 'Script is invalid: {0}'.format( results )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Script "{0}"({1})'.format( self.description, self.name )


@cinp.model()
class BluePrintScript( models.Model ):
  blueprint = models.ForeignKey( BluePrint, on_delete=models.CASCADE )
  script = models.ForeignKey( Script, on_delete=models.CASCADE )
  name = models.CharField( max_length=50 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'BluePrint Script name "{0}" is invalid'.format( self.name )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'BluePrintScript for BluePrint "{0}" Named "{1}" Script "{2}"'.format( self.blueprint, self.name, self.script )

  class Meta:
    unique_together = ( ( 'blueprint', 'name' ), )


@cinp.model()
class PXE( models.Model ):
  name = models.CharField( max_length=50, primary_key=True )
  script = models.TextField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'PXE "{0}"'.format( self.name, self.script )
