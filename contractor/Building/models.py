import uuid

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, JSONField, name_regex
from contractor.Site.models import Site
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint
from contractor.Utilities.models import Networked, PhysicalNetworkInterface

# this is where the plan meats the resources to make it happen, the actuall impelemented thing, and these represent things, you can't delete the records without cleaning up what ever they are pointing too

cinp = CInP( 'Building', '0.1' )


@cinp.model( property_list=( 'state', 'type' ) )
class Foundation( models.Model ):
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it
  blueprint = models.ForeignKey( FoundationBluePrint, on_delete=models.PROTECT )
  locator = models.CharField( max_length=100, unique=True )
  id_map = JSONField( blank=True ) # ie a dict of asset, chassis, system, etc types
  interfaces = models.ManyToManyField( PhysicalNetworkInterface, through='FoundationNetworkInterface' )
  located_at = models.DateTimeField( editable=False, blank=True, null=True )
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def setLocated( self ):
    try:
      self.structure.setDestroyed() #TODO: this may be a little harsh
    except Structure.DoesNotExist:
      pass
    self.located_at = timezone.now()
    self.built_at = None
    self.save()

  def setBuilt( self ):
    self.built_at = timezone.now()
    self.save()

  def setDestroyed( self ):
    try:
      self.structure.setDestroyed() #TODO: this may be a little harsh
    except Structure.DoesNotExist:
      pass
    self.built_at = None
    self.located_at = None
    self.save()

  @property
  def manager( self ):
    return ( None, None ) # manager type, manager paramanter

  @property
  def type( self ):
    return 'Foundation'

  @property
  def canAutoLocate( self ): # child models can decide if it can auto submit job for building, ie: vm (and like foundations) are only canBuild if their structure is auto_build
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

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Foundation #{0} of "{1}" in "{2}"'.format( self.pk, self.blueprint.pk, self.site.pk )


@cinp.model( )
class FoundationNetworkInterface( models.Model ):
  foundation = models.ForeignKey( Foundation )
  interface = models.ForeignKey( PhysicalNetworkInterface )
  name = models.CharField( max_length=20 )
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
  blueprint = models.ForeignKey( StructureBluePrint, on_delete=models.PROTECT ) # ie what to bild
  foundation = models.OneToOneField( Foundation, on_delete=models.PROTECT )   # ie what to build it on
  config_uuid = models.CharField( max_length=36, default=getUUID, unique=True ) # unique
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
    self.config_uuid = str( uuid.uuid4() )
    self.save()

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

  def __str__( self ):
    return 'Structure #{0} of "{1}" in "{2}"'.format( self.pk, self.blueprint.pk, self.site.pk )


@cinp.model( )
class Complex( models.Model ):  # group of Structures, ie a cluster
  name = models.CharField( max_length=20, primary_key=True )
  site = models.ForeignKey( Site, on_delete=models.CASCADE )
  description = models.CharField( max_length=200 )
  members = models.ManyToManyField( Structure )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def isUsable( self ):
    state_list = [ i.state for i in self.members.all() ]

    return 'built' in state_list

  def clean( self, *args, **kwargs ): # also need to make sure a Structure is in only one complex
    super().clean( *args, **kwargs )
    errors = {}
    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'Complex name "{0}" is invalid'.format( self.name )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Complex "{0}"({1})'.format( self.description, self.name )
