import uuid

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

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


@cinp.model( property_list=( 'state', 'type', 'class_list', 'can_auto_locate' ) )
class Foundation( models.Model ):
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it
  blueprint = models.ForeignKey( FoundationBluePrint, on_delete=models.PROTECT )
  locator = models.CharField( max_length=100, unique=True )
  config_values = MapField( blank=True )
  id_map = JSONField( blank=True )  # ie a dict of asset, chassis, system, etc types
  interfaces = models.ManyToManyField( RealNetworkInterface, through='FoundationNetworkInterface' )
  located_at = models.DateTimeField( editable=False, blank=True, null=True )
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def setLocated( self ):
    try:
      self.structure.setDestroyed()  # TODO: this may be a little harsh
    except Structure.DoesNotExist:
      pass
    self.located_at = timezone.now()
    self.built_at = None
    self.save()

  def setBuilt( self ):
    if self.located_at is None:
      self.located_at = timezone.now()
    self.built_at = timezone.now()
    self.save()

  def setDestroyed( self ):
    try:
      self.structure.setDestroyed()  # TODO: this may be a little harsh
    except Structure.DoesNotExist:
      pass
    self.built_at = None
    self.located_at = None
    self.save()

  @staticmethod
  def getTscriptValues( write_mode=False ):  # locator is handled seperatly
    return {  # none of these base items are writeable, ignore the write_mode for now
              'id': ( lambda foundation: foundation.pk, None ),
              'type': ( lambda foundation: foundation.subclass.type, None ),
              'site': ( lambda foundation: foundation.site.pk, None ),
              'blueprint': ( lambda foundation: foundation.blueprint.pk, None ),
              'id_map': ( lambda foundation: foundation.ip_map, None ),
              'interface_list': ( lambda foundation: [ i for i in foundation.interfaces.all() ], None )
            }

  @staticmethod
  def getTscriptFunctions():
    return {}

  def configValues( self ):
    return {
              'foundation_id': self.pk,
              'foundation_type': self.type,
              'foundation_state': self.state,
              'foundation_class_list': self.class_list
            }

  @property
  def subclass( self ):
    for attr in FOUNDATION_SUBCLASS_LIST:
      try:
        return getattr( self, attr )
      except AttributeError:
        pass

    return self

  @cinp.action( { 'type': 'String', 'is_array': True } )
  @staticmethod
  def getFoundationTypes():
    return FOUNDATION_SUBCLASS_LIST

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

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self.subclass )

  @property
  def type( self ):
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
  def checkAuth( user, method, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.type not in self.blueprint.foundation_type_list:
      errors[ 'name' ] = 'Blueprint "{0}" does not list this type ({1})'.format( self.blueprint.description, self.type )

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Foundation #{0} of "{1}" in "{2}"'.format( self.pk, self.blueprint.pk, self.site.pk )


@cinp.model( )
class FoundationNetworkInterface( models.Model ):
  foundation = models.ForeignKey( Foundation )
  interface = models.ForeignKey( RealNetworkInterface )
  physical_location = models.CharField( max_length=100 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
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
  build_priority = models.IntegerField( default=100 )
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

  def configValues( self ):
    return {
             'hostname': self.hostname,
             'structure': self.pk,
             'state': self.state,
             'config_uuid': self.config_uuid
           }

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @property
  def state( self ):
    if self.built_at is not None:
      return 'built'

    return 'planned'

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return Structure.objects.filter( site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.foundation.blueprint not in self.blueprint.combined_foundation_blueprint_list:
      errors[ 'foundation' ] = 'The blueprint "{0}" is not allowed on foundation "{1}"'.format( self.blueprint.description, self.foundation.blueprint.description )

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Structure #{0} of "{1}" in "{2}"'.format( self.pk, self.blueprint.pk, self.site.pk )


@cinp.model( property_list=( 'state', 'type' ) )
class Complex( models.Model ):  # group of Structures, ie a cluster
  name = models.CharField( max_length=40, primary_key=True )
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

    if ( sum( state_list ) * 100 ) / len( state_list ) >= self.built_percentage:
      return 'built'

    return 'planned'

  @property
  def type( self ):
    return 'Unknown'

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return Complex.objects.filter( site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
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

  def configValues( self ):
    return {
              'complex_id': self.pk,
              'complex_type': self.type,
              'complex_state': self.state,
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
    return 'Unknown'

  @property
  def state( self ):
    return 'Built'

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
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
  LINK_OPTIONS = ( ( 'soft', 'soft' ), ( 'hard', 'hard' ) )  # a hardlink if the structure is set back pulls the foundation back with it, soft does not
  foundation = models.ForeignKey( Foundation, on_delete=models.CASCADE )  # this is what id depending
  structure = models.ForeignKey( Structure, on_delete=models.CASCADE )  # depending on this
  link = models.CharField( max_length=4, choices=LINK_OPTIONS )
  script_name = models.CharField( max_length=40, blank=True, null=True )   # optional script name, this job must complete before built_at is set
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def setBuilt( self ):
    self.built_at = timezone.now()
    self.save()

  def setDestroyed( self ):
    self.built_at = None
    self.save()
    if self.link == 'hard':
      self.foundation.setDestroyed()

  @property
  def state( self ):
    if self.built_at is not None:
      return 'built'

    return 'planned'

  @cinp.list_filter( name='foundation', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Building.models.Foundation' } ] )
  @staticmethod
  def filter_foundation( foundation ):
    return Dependancy.objects.filter( foundation=foundation )

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return Dependancy.objects.filter( foundation__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.script_name is not None and not name_regex.match( self.script_name ):
      errors[ 'script_name' ] = '"{0}" is invalid'.format( self.script_name )

    if errors:
      raise ValidationError( errors )

  class Meta:
    unique_together = ( ( 'structure', 'foundation' ), )

  def __str__( self ):
    return 'Dependancy of "{0}" on "{1}"'.format( self.foundation, self.structure )
