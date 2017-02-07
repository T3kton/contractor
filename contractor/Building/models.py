from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, name_regex
from contractor.Site.models import Site
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint
from contractor.Utilities.models import Networked, PhysicalNetworkInterface

# this is where the plan meats the resources to make it happen, the actuall impelemented thing, and these represent things, you can't delete the records without cleaning up what ever they are pointing too

cinp = CInP( 'Building', '0.1' )


@cinp.model( )
class Foundation( models.Model ):
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it
  blueprint = models.ForeignKey( FoundationBluePrint, on_delete=models.PROTECT )
  locator = models.CharField( max_length=100 )
  id_map = MapField( blank=True ) # ie a dict of asset, chassis, system, etc types
  interfaces = models.ManyToManyField( PhysicalNetworkInterface, through='FoundationNetworkInterface' )
  located_at = models.DateTimeField( editable=False, blank=True, null=True )
  built_at = models.DateTimeField( editable=False, blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def setLocated( self ):
    self.located_at = timezone.now()
    self.save()

  def setBuilt( self ):
    self.built_at = timezone.now()
    self.save()

  def setDestroyed( self ):
    self.built_at = None
    self.save()

  @property
  def manager( self ):
    return ( None, None ) # manager type, manager paramanter

  @property
  def state( self ):
    if self.located_at is None:
      return 'planned'

    elif self.located_at is not None and self.built_at is None:
      return 'located'

    return 'built'

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


@cinp.model( )
class Structure( Networked ):
  blueprint = models.ForeignKey( StructureBluePrint, on_delete=models.PROTECT ) # ie what to bild
  foundation = models.ForeignKey( Foundation, on_delete=models.PROTECT )   # ie what to build it on
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
    self.save()

  @property
  def state( self ):
    if self.built_at is None:
      return 'planned'

    return 'built'

  @property
  def config( self ):
    # combine all the config stuffs
    return {}

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
    if not name_regex.match( self.name ):
      raise ValidationError( 'Complex name "{0}" is invalid'.format( self.name ) )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Complex "{0}"({1})'.format( self.description, self.name )
