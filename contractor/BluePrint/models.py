from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, JSONField, StringListField, name_regex, config_name_regex
from contractor.tscript import parser
from contractor.lib.config import getConfig

# these are the templates, describe how soomething is made and the template of the thing it's made on

cinp = CInP( 'BluePrint', '0.1' )


class BluePrintException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'class': 'BluePrintException', 'error': self.code, 'message': self.message }

  def __str__( self ):
    return 'BluePrintException ({0}): {1}'.format( self.code, self.message )


@cinp.model( not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE' ] )
class BluePrint( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )  # update Architect if this changes max_length
  description = models.CharField( max_length=200 )
  scripts = models.ManyToManyField( 'Script', through='BluePrintScript' )
  config_values = MapField( blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def get_script( self, name ):
    try:
      return self.blueprintscript_set.get( name=name ).script.script
    except BluePrintScript.DoesNotExist:
      for parent in self.parent_list.all():
        tmp = parent.get_script( name )
        if tmp is not None:
          return tmp

      return None

  @property
  def subclass( self ):
    try:
      return self.foundationblueprint
    except AttributeError:
      pass

    try:
      return self.structureblueprint
    except AttributeError:
      pass

    return self

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self.subclass )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if verb == 'DESCRIBE':
      return True

    return False

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):  # if this regex changes, make sure to update tcalc parser in archetect
      errors[ 'name' ] = 'BluePrint Script name "{0}" is invalid'.format( self.name )

    for name in self.config_values:
      if not config_name_regex.match( name ):
        errors[ 'config_values' ] = 'config item name "{0}" is invalid'.format( name )
        break

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'BluePrint "{0}"({1})'.format( self.description, self.name )


# this has the template to define what to match to, weither it be a piece of hardware, a complex of some type
# this is then used to prepare that vm/blade/device in a non blueprint specific way
# the material is not associated with the sctructure until fully prepared
# ipmi type ip addresses will belong to the material, they belong to the device not the OS on the device anyway
# will need a working pool of "eth0" type ips for the prepare
@cinp.model( property_list=( 'subcontractor', ) )
class FoundationBluePrint( BluePrint ):
  parent_list = models.ManyToManyField( 'self', blank=True, symmetrical=False )
  foundation_type_list = StringListField( max_length=200 )  # list of the foundation types this blueprint can be used for
  template = JSONField( default={}, blank=True )
  physical_interface_names = StringListField( max_length=200, blank=True )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @property
  def subcontractor( self ):
    return { 'type': None }

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not isinstance( self.template, dict ):
      errors[ 'template' ] = 'template must be a dict'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'FoundationBluePrint "{0}"({1})'.format( self.description, self.name )


@cinp.model(  )
class StructureBluePrint( BluePrint ):
  parent_list = models.ManyToManyField( 'self', blank=True, symmetrical=False )  # TODO: go through a "through" field and have a foundation class select which parent, this way there can be a container parent and a VM parent and simmaler
  foundation_blueprint_list = models.ManyToManyField( FoundationBluePrint )  # list of possible foundations this blueprint could be implemented on

  @property
  def combined_foundation_blueprint_list( self ):
    result = list( self.foundation_blueprint_list.all() )
    for parent in self.parent_list.all():
      result += parent.combined_foundation_blueprint_list

    return list( set( result ) )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'StructureBluePrint "{0}"({1})'.format( self.description, self.name )


@cinp.model()
class Script( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )  # if this changes update the Post.script_name in the PostOffice
  description = models.CharField( max_length=200 )
  script = models.TextField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

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

  def __str__( self ):
    return 'Script "{0}"({1})'.format( self.description, self.name )


@cinp.model()
class BluePrintScript( models.Model ):
  blueprint = models.ForeignKey( BluePrint, on_delete=models.CASCADE )
  script = models.ForeignKey( Script, on_delete=models.CASCADE )
  name = models.CharField( max_length=50 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'BluePrint Script name "{0}" is invalid'.format( self.name )

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'blueprint', 'name' ), )

  def __str__( self ):
    return 'BluePrintScript for BluePrint "{0}" Named "{1}" Script "{2}"'.format( self.blueprint, self.name, self.script )


@cinp.model()
class PXE( models.Model ):
  name = models.CharField( max_length=50, primary_key=True )
  boot_script = models.TextField()
  template = models.TextField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'PXE "{0}"'.format( self.name, self.script )
