import uuid

from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, JSONField, name_regex, config_name_regex
from contractor.Site.models import Site
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint
from contractor.Utilities.models import Networked
from contractor.lib.config import getConfig, mergeValues
from contractor.Records.lib import post_save_callback, post_delete_callback

# this is where the plan meats the resources to make it happen, the actuall impelemented thing, and these represent things, you can't delete the records without cleaning up what ever they are pointing too

cinp = CInP( 'Building', '0.1' )

FOUNDATION_SUBCLASS_LIST = []
COMPLEX_SUBCLASS_LIST = []


class BuildingException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'class': 'BuildingException', 'error': self.code, 'message': self.message }

  def __str__( self ):
    return 'BuildingException ({0}): {1}'.format( self.code, self.message )


@cinp.model( property_list=( 'state', 'type', 'class_list', { 'name': 'attached_structure', 'type': 'Model', 'model': 'contractor.Building.models.Structure' } ), not_allowed_verb_list=[ 'CREATE', 'UPDATE' ] )
class Foundation( models.Model ):
  locator = models.CharField( max_length=100, primary_key=True )  # if this changes make sure to update architect - instance - foundation_id
  site = models.ForeignKey( Site, on_delete=models.PROTECT )
  blueprint = models.ForeignKey( FoundationBluePrint, on_delete=models.PROTECT )
  id_map = JSONField( blank=True, null=True )  # ie a dict of asset, chassis, system, etc types
  located_at = models.DateTimeField( editable=False, blank=True, null=True )
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.action()
  def setLocated( self ):
    """
    Sets the Foundation to 'located' state.  This will not create a destroy job.

    NOTE: This will set the attached structure (if there is one) to 'planned' without running a job to destroy the structure.
    """
    try:
      self.structure.setDestroyed()  # TODO: this may be a little harsh
    except AttributeError:
      pass
    self.located_at = timezone.now()
    self.built_at = None
    self.save()

  @cinp.action()
  def setBuilt( self ):
    """
    Set the Foundation to 'built' state.  This will not create a create job.
    """
    if self.located_at is None:
      self.located_at = timezone.now()
    self.built_at = timezone.now()
    self.save()

  @cinp.action()
  def setDestroyed( self ):
    """
    Sets the Foundation to 'destroyed' state.  This will not create a destroy job.

    NOTE: This will set the attached structure (if there is one) to 'planned' without running a job to destroy the structure.
    """
    try:
      self.structure.setDestroyed()  # TODO: this may be a little harsh
    except AttributeError:
      pass
    self.built_at = None
    self.located_at = None
    self.save()

  @cinp.action( return_type='Integer' )
  def doCreate( self ):
    """
    This will submit a job to run the create script.
    """
    from contractor.Foreman.lib import createJob
    return createJob( 'create', self )

  @cinp.action( return_type='Integer' )
  def doDestroy( self ):
    """
    This will submit a job to run the destroy script.
    """
    from contractor.Foreman.lib import createJob
    return createJob( 'destroy', self )

  @staticmethod
  def getTscriptValues( write_mode=False ):  # locator is handled seperatly
    return {  # none of these base items are writeable, ignore the write_mode for now
              'locator': ( lambda foundation: foundation.locator, None ),  # redundant?
              'type': ( lambda foundation: foundation.subclass.type, None ),  # redudnant?
              'site': ( lambda foundation: foundation.site.pk, None ),
              'blueprint': ( lambda foundation: foundation.blueprint.pk, None ),
              # 'ip_map': ( lambda foundation: foundation.ip_map, None ),
              'interface_list': ( lambda foundation: [ i for i in foundation.networkinterface_set.all().order_by( 'physical_location' ) ], None )  # redudntant?
            }

  @staticmethod
  def getTscriptFunctions():
    return {}

  def configAttributes( self ):
    return {
              '_foundation_id': self.pk,
              '_foundation_type': self.type,
              '_foundation_state': self.state,
              '_foundation_class_list': self.class_list,
              '_foundation_locator': self.locator,
              '_foundation_interface_list': [ i.config for i in self.networkinterface_set.all().order_by( 'physical_location' ) ]
            }

  @property
  def subclass( self ):
    for attr in FOUNDATION_SUBCLASS_LIST:
      try:
        return getattr( self, attr )
      except AttributeError:
        pass

    return self

  @property
  def type( self ):
    real = self.subclass
    if real != self:
      return real.type

    return 'Unknown'

  @property
  def class_list( self ):
    # top level generic classes: Metal, VM, Container, Switch, PDU
    return []

  @property
  def complex( self ):
    return None

  @property
  def can_delete( self ):
    try:
      return self.structure.state != 'build'
    except AttributeError:
      pass

    return True

  @property
  def attached_structure( self ):  # TODO: look arround and see if this is used where it should be, or we can remove this
    try:
      return self.structure
    except AttributeError:
      pass

    return None

  @property
  def state( self ):
    if self.located_at is not None and self.built_at is not None:
      return 'built'

    elif self.located_at is not None:
      return 'located'

    return 'planned'

  @property
  def description( self ):
    return self.locator

  @property
  def dependencyId( self ):
    return 'f-{0}'.format( self.pk )

  @cinp.action( { 'type': 'String', 'is_array': True } )
  @staticmethod
  def getFoundationTypes():
    return FOUNDATION_SUBCLASS_LIST

  @cinp.action( return_type='Map' )
  def getConfig( self ):
    """
    returns the computed config for this foundation
    """
    return mergeValues( getConfig( self.subclass ) )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def filter_site( site ):
    return Foundation.objects.filter( site=site )

  @cinp.list_filter( name='todo', paramater_type_list=[ { 'type': 'Model', 'model': Site }, 'Boolean', 'String' ] )
  @staticmethod
  def filter_todo( site, has_dependancies, foundation_class ):
    args = {}
    args[ 'site' ] = site
    if has_dependancies:
      args[ 'dependency' ] = True

    if foundation_class is not None:
      if foundation_class not in FOUNDATION_SUBCLASS_LIST:
        raise ValueError( 'Invalid foundation class' )

      args[ foundation_class ] = True

    return Foundation.objects.filter( **args )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.locator ):
      errors[ 'locator' ] = 'Invalid'

    if self.blueprint_id is not None and self.type not in self.blueprint.foundation_type_list:
        errors[ 'name' ] = 'Blueprint "{0}" does not list this type ({1})'.format( self.blueprint.description, self.type )

    if errors:
      raise ValidationError( errors )

  def delete( self ):
    if not self.can_delete:
      raise models.ProtectedError( 'Structure not Deleatable' )

    subclass = self.subclass

    if self == subclass:
      super().delete()
    else:
      subclass.delete()

  def __str__( self ):
    return 'Foundation #{0}({1}) of "{2}" in "{3}"'.format( self.pk, self.locator, self.blueprint.pk, self.site.pk )


def getUUID():
  return str( uuid.uuid4() )


@cinp.model( property_list=( 'state', ), read_only_list=( 'config_uuid', ) )
class Structure( Networked ):
  blueprint = models.ForeignKey( StructureBluePrint, on_delete=models.PROTECT )  # ie what to bild
  foundation = models.OneToOneField( Foundation, on_delete=models.PROTECT )      # ie what to build it on
  config_uuid = models.CharField( max_length=36, default=getUUID, unique=True )  # unique
  config_values = MapField( blank=True, null=True )
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def setBuilt( self ):
    self.built_at = timezone.now()
    self.save()

  def setDestroyed( self ):
    self.built_at = None
    self.config_uuid = str( uuid.uuid4() )  # new on destroyed, that way we can leave anything that might still be kicking arround in the dust
    self.save()
    for dependency in self.dependency_set.all():
      dependency.setDestroyed()

  def configAttributes( self ):
    provisioning_interface = self.provisioning_interface
    result = {
               '_structure_id': self.pk,
               '_structure_state': self.state,
               '_structure_config_uuid': self.config_uuid,
               '_provisioning_interface': provisioning_interface.name if provisioning_interface is not None else None,
               '_provisioning_interface_mac': provisioning_interface.mac if provisioning_interface is not None else None
             }

    result[ '_hostname' ] = self.hostname
    result[ '_domain_name' ] = self.domain_name
    result[ '_fqdn' ] = self.fqdn
    result[ '_interface_map' ] = {}
    for iface in self.foundation.networkinterface_set.all():  # mabey? mabey not?
      result[ '_interface_map' ][ iface.name ] = iface.config

    return result

  @property
  def state( self ):
    if self.built_at is not None:
      return 'built'

    return 'planned'

  @property
  def can_delete( self ):
    return self.state != 'build'

  @property
  def description( self ):
    return self.hostname

  @property
  def dependencyId( self ):
    return 's-{0}'.format( self.pk )

  @cinp.action( return_type='Integer' )
  def doCreate( self ):
    from contractor.Foreman.lib import createJob
    return createJob( 'create', self )

  @cinp.action( return_type='Integer' )
  def doDestroy( self ):
    from contractor.Foreman.lib import createJob
    return createJob( 'destroy', self )

  @cinp.action( return_type='Map' )
  def getConfig( self ):
    return mergeValues( getConfig( self ) )

  @cinp.action( return_type='Map', paramater_type_list=[ 'Map' ] )
  def updateConfig( self, config_value_map ):  # TODO: this is a bad Idea, need to figure out a better way to do this, at least restrict it to accounts that can create/updatre structures
    self.config_values.update( config_value_map )
    self.full_clean()
    self.save()

    return mergeValues( getConfig( self ) )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def filter_site( site ):
    return Structure.objects.filter( site=site )

  @cinp.list_filter( name='complex', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Complex' } ] )
  @staticmethod
  def filter_complex( complex ):
    return complex.members.all()

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.foundation_id is not None and self.foundation.blueprint not in self.blueprint.combined_foundation_blueprint_list:
      errors[ 'foundation' ] = 'The blueprint "{0}" is not allowed on foundation "{1}"'.format( self.blueprint.description, self.foundation.blueprint.description )

    if self.config_values is not None:
      for name in self.config_values:
        if not config_name_regex.match( name ):
          errors[ 'config_values' ] = 'config item name "{0}" is invalid'.format( name )
          break

    if errors:
      raise ValidationError( errors )

  def delete( self ):
    if not self.can_delete:
      raise models.ProtectedError( 'Structure not Deleteable' )

    super().delete()

  def __str__( self ):
    return 'Structure #{0}({1}) of "{2}" in "{3}"'.format( self.pk, self.hostname, self.blueprint.pk, self.site.pk )


@cinp.model( property_list=( 'state', 'type' ) )
class Complex( models.Model ):  # group of Structures, ie a cluster
  name = models.CharField( max_length=40, primary_key=True )  # update Architect if this changes max_length
  site = models.ForeignKey( Site, on_delete=models.CASCADE )
  description = models.CharField( max_length=200 )
  members = models.ManyToManyField( Structure, through='ComplexStructure' )
  built_percentage = models.IntegerField( default=90 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def subclass( self ):
    for attr in COMPLEX_SUBCLASS_LIST:
      try:
        return getattr( self, attr )
      except AttributeError:
        pass

    return self

  @property
  def state( self ):
    state_list = [ 1 if i.state == 'built' else 0 for i in self.members.all() ]

    if len( state_list ) == 0:
      return 'planned'

    if ( sum( state_list ) * 100 ) / len( state_list ) >= self.built_percentage:
      return 'built'

    return 'planned'

  @property
  def type( self ):
    real = self.subclass
    if real != self:
      return real.type

    return 'Unknown'

  @property
  def dependencyId( self ):
    return 'c-{0}'.format( self.pk )

  def configAttributes( self ):
    return {}

  def newFoundation( self, hostname ):
    raise ValueError( 'Root Complex dose not support Foundations' )

  @cinp.action( return_type={ 'type': 'Model', 'model': Foundation }, paramater_type_list=[ { 'type': 'String' } ] )
  def createFoundation( self, hostname ):  # TODO: wrap this in a transaction, or some other way to unwrap everything if it fails
    self = self.subclass

    foundation = self.newFoundation( hostname )  # also need to create the network interfaces
    return foundation

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def filter_site( site ):
    return Complex.objects.filter( site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = '"{0}" is invalid'.format( self.name[ 0:50 ] )

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Complex "{0}"({1})'.format( self.description, self.name )


@cinp.model( )
class ComplexStructure( models.Model ):
  complex = models.ForeignKey( Complex )
  structure = models.ForeignKey( Structure )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @staticmethod
  def getTscriptValues( write_mode=False ):  # locator is handled seperatly
    return {  # none of these base items are writeable, ignore the write_mode for now
              'id': ( lambda foundation: foundation.pk, None ),
              'type': ( lambda foundation: foundation.subclass.type, None ),
              'site': ( lambda foundation: foundation.site.pk, None )
            }

  @staticmethod
  def getTscriptFunctions():
    return {}

  def configAttributes( self ):
    return {
              '_complex_id': self.pk,
              '_complex_type': self.type,
              '_complex_state': self.state,
            }

  @property
  def subclass( self ):
    for attr in COMPLEX_SUBCLASS_LIST:
      try:
        return getattr( self, attr )
      except AttributeError:
        pass

    return self

  # @cinp.action( return_type='String' )
  # def getRealFoundationURI( self ):  # TODO: this is such a hack, figure  out a better way
  #   subclass = self.subclass
  #   class_name = type( subclass ).__name__
  #   if class_name == 'Foundation':
  #     return '/api/v1/Building/Foundation:{0}:'.format( subclass.pk )
  #
  #   elif class_name == 'VirtualBoxFoundation':
  #     return '/api/v1/VirtualBox/VirtualBoxFoundation:{0}:'.format( subclass.pk )
  #
  #   elif class_name == 'ManualFoundation':
  #     return '/api/v1/Manual/ManualFoundation:{0}:'.format( subclass.pk )
  #
  #   raise ValueError( 'Unknown Foundation class "{0}"'.format( class_name ) )
  #
  @cinp.action( return_type='Map' )
  def getConfig( self ):
    return mergeValues( getConfig( self.subclass ) )

  @property
  def type( self ):
    real = self.subclass
    if real != self:
      return real.type

    return 'Unknown'

  @property
  def state( self ):
    return 'Built'

  @cinp.list_filter( name='complex', paramater_type_list=[ { 'type': 'Model', 'model': Complex } ] )
  @staticmethod
  def filter_complex( complex ):
    return ComplexStructure.objects.filter( complex=complex )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  # TODO: need to make sure a Structure is in only one complex
  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'ComplexStructure for "{0}" to "{1}"'.format( self.complex, self.structure )


@cinp.model( property_list=( 'state', ) )
class Dependency( models.Model ):
  LINK_CHOICES = ( 'soft', 'hard' )  # a hardlink if the structure is set back pulls the foundation back with it, soft does not
  structure = models.ForeignKey( Structure, on_delete=models.CASCADE, blank=True, null=True )  # depending on this
  dependency = models.ForeignKey( 'self', on_delete=models.CASCADE, related_name='+', blank=True, null=True )  # or this
  foundation = models.OneToOneField( Foundation, on_delete=models.CASCADE, blank=True, null=True )  # this is what is depending
  script_structure = models.ForeignKey( Structure, on_delete=models.CASCADE, related_name='+', blank=True, null=True )  # if this is specified, the script runs on this
  link = models.CharField( max_length=4, choices=[ ( i, i ) for i in LINK_CHOICES ] )
  create_script_name = models.CharField( max_length=40, blank=True, null=True )   # optional script name, this job must complete before built_at is set
  destroy_script_name = models.CharField( max_length=40, blank=True, null=True )   # optional script name, this job is run before destroying
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def setBuilt( self ):
    self.built_at = timezone.now()
    self.save()

  def setDestroyed( self ):
    self.built_at = None
    self.save()
    for dependency in Dependency.objects.filter( dependency=self ):
      dependency.setDestroyed()

    if self.link == 'hard':
      if self.foundation is not None:
        self.foundation.setDestroyed()  # TODO: Destroyed or Identified?

  @property
  def state( self ):
    if self.built_at is not None:
      return 'built'

    return 'planned'

  @property
  def can_delete( self ):
    return self.state != 'build'

  @property
  def site( self ):
    if self.foundation is not None:
      return self.foundation.site
    elif self.script_structure is not None:
      return self.script_structure.site
    elif self.dependency is not None:
      return self.dependency.site
    else:
      return self.structure.site

  @property
  def blueprint( self ):
    if self.script_structure is not None:
      return self.script_structure.blueprint
    else:
      return self.structure.blueprint

  @property
  def description( self ):
    left = None
    if self.structure is not None:
      left = self.structure.hostname
    else:
      left = self.dependency.description

    right = ''
    if self.foundation is not None:
      right = self.foundation.locator

    return '{0}-{1}'.format( left, right )

  @property
  def dependencyId( self ):
    return 'd-{0}'.format( self.pk )

  @cinp.list_filter( name='foundation', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Foundation' } ] )
  @staticmethod
  def filter_foundation( foundation ):
    return Dependency.objects.filter( foundation=foundation )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def filter_site( site ):
    return Dependency.objects.filter( Q( foundation__site=site ) |
                                      Q( foundation__isnull=True, script_structure__site=site ) |
                                      Q( foundation__isnull=True, script_structure__isnull=True, dependency__structure__site=site ) |
                                      Q( foundation__isnull=True, script_structure__isnull=True, structure__site=site )
                                      )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.dependency is None and self.structure is None:
      errors[ 'structure' ] = 'Either structure or dependency is required'

    if self.structure is None and self.script_structure is None:
      if self.create_script_name is not None:
        errors[ 'create_script_name' ] = 'structure or script_sctructure are required for scripts'

      if self.destroy_script_name is not None:
        errors[ 'destroy_script_name' ] = 'structure or script_sctructure are required for scripts'

    if self.create_script_name is not None and not name_regex.match( self.create_script_name ):
      errors[ 'create_script_name' ] = '"{0}" is invalid'.format( self.create_script_name )

    if self.destroy_script_name is not None and not name_regex.match( self.destroy_script_name ):
      errors[ 'destroy_script_name' ] = '"{0}" is invalid'.format( self.destroy_script_name )

    if self.destroy_script_name is not None and self.destroy_script_name == self.create_script_name:
      errors[ 'destroy_script_name' ] = 'destroy and create script must be different'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    structure = None
    if self.structure is not None:
      structure = self.structure
    else:
      structure = self.dependency.structure

    return 'Dependency of "{0}" on "{1}"'.format( self.foundation, structure )


post_save.connect( post_save_callback, sender=Foundation )
post_save.connect( post_save_callback, sender=Structure )
post_delete.connect( post_delete_callback, sender=Foundation )
post_delete.connect( post_delete_callback, sender=Structure )
