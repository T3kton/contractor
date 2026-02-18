from django.db import models
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, StringListField, name_regex, config_name_regex
from contractor.tscript import parser
from contractor.lib.config import getConfig
from contractor.BluePrint.lib import validateTemplate
from contractor.Records.lib import post_save_callback, post_delete_callback


cinp = CInP( 'BluePrint', '0.1' )


class BluePrintException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'exception': 'BluePrintException', 'error': self.code, 'message': self.message }

  def __str__( self ):
    return 'BluePrintException ({0}): {1}'.format( self.code, self.message )


@cinp.model( not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE' ], property_list=( { 'name': 'script_map', 'type': 'Map' }, ), hide_field_list=( 'scripts', ) )
class BluePrint( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )  # update Architect and MCP if this changes max_length
  description = models.CharField( max_length=200 )
  scripts = models.ManyToManyField( 'Script', through='BluePrintScript' )
  config_values = MapField( blank=True, null=True )
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
  def script_map( self ):
    result = {}
    for blueprintscript in self.blueprintscript_set.all():
      result[ blueprintscript.name ] = blueprintscript.script

    return result

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
    return cinp.basic_auth_check( user, verb, action, BluePrint, { 'getConfig': None } )  # TODO: when 'view' permission becomes optional, tie getConfig to it

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):  # if this regex changes, make sure to update tcalc parser in archetect
      errors[ 'name' ] = 'invalid'

    if self.config_values is not None:
      for name in self.config_values:
        if not config_name_regex.match( name ):
          errors[ 'config_values' ] = 'config item name "{0}" is invalid'.format( name )
          break

    if errors:
      raise ValidationError( errors )

  class Meta:
    default_permissions = ()  # only CALL

  def __str__( self ):
    return 'BluePrint "{0}"({1})'.format( self.description, self.name )


# this has the template to define what to match to, weither it be a piece of hardware, a complex of some type
# this is then used to prepare that vm/blade/device in a non blueprint specific way
# the material is not associated with the sctructure until fully prepared
# ipmi type ip addresses will belong to the material, they belong to the device not the OS on the device anyway
# will need a working pool of "eth0" type ips for the prepare
@cinp.model( property_list=( { 'name': 'script_map', 'type': 'Map' }, ), hide_field_list=( 'scripts', ) )
class FoundationBluePrint( BluePrint ):
  parent_list = models.ManyToManyField( 'self', blank=True, symmetrical=False )
  foundation_type_list = StringListField( max_length=200 )  # list of the foundation types this blueprint can be used for
  validation_template = MapField( blank=True, null=True )
  physical_interface_names = StringListField( max_length=200, blank=True )

  def getValidationTemplate( self ):
    if self.validation_template:
      return self.validation_template

    for parent in self.parent_list.all():
      tmp = parent.getValidationTemplate()
      if tmp is not None:
        return tmp

    return None

  def validateIdMap( self, id_map ):
    template = self.getValidationTemplate()
    if template is None:
      return None

    return validateTemplate( id_map, template )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, action, FoundationBluePrint, { 'getConfig': None } )  # TODO: when 'view' permission becomes optional, tie getConfig to it

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not isinstance( self.validation_template, dict ):
      errors[ 'validation_template' ] = 'template must be a dict'

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'FoundationBluePrint "{0}"({1})'.format( self.description, self.name )


@cinp.model( property_list=( { 'name': 'script_map', 'type': 'Map' }, ), hide_field_list=( 'scripts', ) )
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
    return cinp.basic_auth_check( user, verb, action, StructureBluePrint, { 'getConfig': None } )  # TODO: when 'view' permission becomes optional, tie getConfig to it

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

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
    return cinp.basic_auth_check( user, verb, action, Script )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'invalid'

    results = parser.lint( self.script )
    if results is not None:
      errors[ 'script' ] = 'invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'Script "{0}"({1})'.format( self.description, self.name )


@cinp.model()
class BluePrintScript( models.Model ):
  blueprint = models.ForeignKey( BluePrint, on_delete=models.CASCADE )
  script = models.ForeignKey( Script, on_delete=models.CASCADE )
  name = models.CharField( max_length=50 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.list_filter( name='blueprint', paramater_type_list=[ { 'type': 'Model', 'model': BluePrint } ] )
  @staticmethod
  def filter_site( blueprint ):
    return BluePrintScript.objects.filter( blueprint=blueprint )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return cinp.basic_auth_check( user, verb, action, BluePrintScript )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'blueprint', 'name' ), )
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

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
    return cinp.basic_auth_check( user, verb, action, PXE )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'PXE "{0}"'.format( self.name )


post_save.connect( post_save_callback, sender=FoundationBluePrint )
post_save.connect( post_save_callback, sender=StructureBluePrint )
post_delete.connect( post_delete_callback, sender=FoundationBluePrint )
post_delete.connect( post_delete_callback, sender=StructureBluePrint )
