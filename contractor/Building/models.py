import uuid

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, JSONField, name_regex
from contractor.Site.models import Site
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint
from contractor.Utilities.models import Networked, RealNetworkInterface
from contractor.lib.config import getConfig

# this is where the plan meats the resources to make it happen, the actuall impelemented thing, and these represent things, you can't delete the records without cleaning up what ever they are pointing too

cinp = CInP( 'Building', '0.1' )

FOUNDATION_SUBCLASS_LIST = []
COMPLEX_SUBCLASS_LIST = []


@cinp.model( property_list=( 'state', 'type', 'class_list', 'can_auto_locate' ), not_allowed_verb_list=[ 'CREATE', 'DELETE', 'UPDATE' ] )
class Foundation( models.Model ):
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it
  blueprint = models.ForeignKey( FoundationBluePrint, on_delete=models.PROTECT )
  locator = models.CharField( max_length=100, unique=True )
  id_map = JSONField( blank=True )  # ie a dict of asset, chassis, system, etc types
  interfaces = models.ManyToManyField( RealNetworkInterface, through='FoundationNetworkInterface' )
  located_at = models.DateTimeField( editable=False, blank=True, null=True )
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.action()
  def setLocated( self ):
    try:
      self.structure.setDestroyed()  # TODO: this may be a little harsh
    except Structure.DoesNotExist:
      pass
    self.located_at = timezone.now()
    self.built_at = None
    self.save()

  @cinp.action()
  def setBuilt( self ):
    if self.located_at is None:
      self.located_at = timezone.now()
    self.built_at = timezone.now()
    self.save()

  @cinp.action()
  def setDestroyed( self ):
    try:
      self.structure.setDestroyed()  # TODO: this may be a little harsh
    except Structure.DoesNotExist:
      pass
    self.built_at = None
    self.located_at = None
    self.save()

  @cinp.action( return_type='Integer' )
  def doCreate( self ):
    from contractor.Foreman.lib import createJob
    return createJob( 'create', self )

  @cinp.action( return_type='Integer' )
  def doDestroy( self ):
    from contractor.Foreman.lib import createJob
    return createJob( 'destroy', self )

  @staticmethod
  def getTscriptValues( write_mode=False ):  # locator is handled seperatly
    return {  # none of these base items are writeable, ignore the write_mode for now
              'locator': ( lambda foundation: foundation.locator, None ),
              'type': ( lambda foundation: foundation.subclass.type, None ),
              'site': ( lambda foundation: foundation.site.pk, None ),
              'blueprint': ( lambda foundation: foundation.blueprint.pk, None ),
              # 'ip_map': ( lambda foundation: foundation.ip_map, None ),
              'interface_list': ( lambda foundation: [ i for i in foundation.interfaces.all() ], None )
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
              '_foundation_interface_list': [ i.name for i in self.interfaces.all() ]
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
  def can_auto_locate( self ):  # child models can decide if it can auto submit job for building, ie: vm (and like foundations) are only canBuild if their structure is auto_build
    return False

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
  def dependancyId( self ):
    return 'f-{0}'.format( self.pk )

  @cinp.action( { 'type': 'String', 'is_array': True } )
  @staticmethod
  def getFoundationTypes():
    return FOUNDATION_SUBCLASS_LIST

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self.subclass )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return Foundation.objects.filter( site=site )

  @cinp.list_filter( name='todo', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' }, 'Boolean', 'Boolean', 'String' ] )
  @staticmethod
  def filter_todo( site, auto_build, has_dependancies, foundation_class ):
    args = {}
    args[ 'site' ] = site
    if has_dependancies:
      args[ 'dependancy' ] = True

    if foundation_class is not None:
      if foundation_class not in FOUNDATION_SUBCLASS_LIST:
        raise ValueError( 'Invalid foundation class' )

      args[ foundation_class ] = True

    return Foundation.objects.filter( **args  )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.type not in self.blueprint.foundation_type_list:
      errors[ 'name' ] = 'Blueprint "{0}" does not list this type ({1})'.format( self.blueprint.description, self.type )

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Foundation #{0}({1}) of "{2}" in "{3}"'.format( self.pk, self.locator, self.blueprint.pk, self.site.pk )


@cinp.model( )
class FoundationNetworkInterface( models.Model ):
  foundation = models.ForeignKey( Foundation )
  interface = models.ForeignKey( RealNetworkInterface )
  physical_location = models.CharField( max_length=100 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'FoundationNetworkInterface for "{0}" to "{1}" named "{2}"'.format( self.foundation, self.interface, self.name )


def getUUID():
  return str( uuid.uuid4() )


@cinp.model( property_list=( 'state', ), read_only_list=( 'config_uuid', ) )
class Structure( Networked ):
  blueprint = models.ForeignKey( StructureBluePrint, on_delete=models.PROTECT )  # ie what to bild
  foundation = models.OneToOneField( Foundation, on_delete=models.PROTECT )      # ie what to build it on
  config_uuid = models.CharField( max_length=36, default=getUUID, unique=True )  # unique
  config_values = MapField( blank=True )
  auto_build = models.BooleanField( default=True )
  # build_priority = models.IntegerField( default=100 )
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
    for dependancy in self.dependancy_set.all():
      dependancy.setDestroyed()

  def configAttributes( self ):
    result = {
               '_structure_id': self.pk,
               '_structure_state': self.state,
               '_structure_config_uuid': self.config_uuid,
             }

    result[ 'hostname' ] = self.hostname
    result[ 'network' ] = {}
    for address in self.networked_ptr.address_set.all():
      tmp = {
              'ip_address': address.ip_address,
              'netmask': address.netmask,
              'prefix': address.prefix,
              'network': address.network,
              'gateway': address.gateway
            }

      if tmp[ 'gateway' ] is None:
        del tmp[ 'gateway' ]

      result[ 'network' ][ address.interface_name ] = tmp

    return result

  @property
  def state( self ):
    if self.built_at is not None:
      return 'built'

    return 'planned'

  @property
  def description( self ):
    return self.hostname

  @property
  def dependancyId( self ):
    return 's-{0}'.format( self.pk )

  @cinp.action( return_type='Integer' )
  def doCreate( self ):
    from contractor.Foreman.lib import createJob
    return createJob( 'create', self )

  @cinp.action( return_type='Integer' )
  def doDestroy( self ):
    from contractor.Foreman.lib import createJob
    return createJob( 'destroy', self )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return Structure.objects.filter( site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.foundation.blueprint not in self.blueprint.combined_foundation_blueprint_list:
      errors[ 'foundation' ] = 'The blueprint "{0}" is not allowed on foundation "{1}"'.format( self.blueprint.description, self.foundation.blueprint.description )

    if errors:
      raise ValidationError( errors )

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
  def dependancyId( self ):
    return 'c-{0}'.format( self.pk )

  def configAttributes( self ):
    return {}

  def newFoundation( self, hostname ):
    raise ValueError( 'Root Complex dose not support Foundations' )

  @cinp.action( return_type={ 'type': 'Model', 'model': 'contractor.Building.models.Foundation' }, paramater_type_list=[ { 'type': 'String' } ] )
  def createFoundation( self, hostname ):  # TODO: wrap this in a transaction, or some other way to unwrap everything if it fails
    self = self.subclass
    return self.newFoundation( hostname )  # also need to create the network interfaces

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
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

  # @cinp.action( 'String' )
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
  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self.subclass )

  @property
  def type( self ):
    real = self.subclass
    if real != self:
      return real.type

    return 'Unknown'

  @property
  def state( self ):
    return 'Built'

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
class Dependancy( models.Model ):
  LINK_CHOICES = ( 'soft', 'hard' )  # a hardlink if the structure is set back pulls the foundation back with it, soft does not
  structure = models.ForeignKey( Structure, on_delete=models.CASCADE, blank=True, null=True )  # depending on this
  dependancy = models.ForeignKey( 'self', on_delete=models.CASCADE, related_name='+', blank=True, null=True )  # or this
  foundation = models.OneToOneField( Foundation, on_delete=models.CASCADE, blank=True, null=True )  # this is what id depending
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
    for dependancy in Dependancy.objects.filter( dependancy=self ):
      dependancy.setDestroyed()

    if self.link == 'hard':
      if self.foundation is not None:
        self.foundation.setDestroyed()  # TODO: Destroyed or Identified?

  @property
  def state( self ):
    if self.built_at is not None:
      return 'built'

    return 'planned'

  @property
  def site( self ):
    if self.foundation is not None:
      return self.foundation.site
    elif self.script_structure is not None:
      return self.script_structure.site
    elif self.dependancy is not None:
      return self.dependancy.site
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
      left = self.dependancy.description

    right = ''
    if self.foundation is not None:
      right = self.foundation.locator

    return '{0}-{1}'.format( left, right )

  @property
  def dependancyId( self ):
    return 'd-{0}'.format( self.pk )

  @cinp.list_filter( name='foundation', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Foundation' } ] )
  @staticmethod
  def filter_foundation( foundation ):
    return Dependancy.objects.filter( foundation=foundation )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return Dependancy.objects.filter( Q( foundation__site=site ) |
                                      Q( foundation__isnull=True, script_structure__site=site ) |
                                      Q( foundation__isnull=True, script_structure__isnull=True, dependancy__structure__site=site ) |
                                      Q( foundation__isnull=True, script_structure__isnull=True, structure__site=site )
                                      )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.dependancy is None and self.structure is None:
      errors[ 'structure' ] = 'Either structure or dependancy is required'

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
      structure = self.dependancy.structure

    return 'Dependancy of "{0}" on "{1}"'.format( self.foundation, structure )
