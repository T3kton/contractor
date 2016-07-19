from django.db import models
from django.core.exceptions import ValidationError

from django.utils import timezone

from contractor.fields import JSONField, name_regex, hostname_regex
from contractor.Site.models import Site
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint

# this is where the plan meats the resources to make it happen, the actuall impelemented thing, and these represent things, you can't delete the records without cleaning up what ever they are pointing too

class Foundation( models.Model ):
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it
  blueprint = models.ForeignKey( FoundationBluePrint, on_delete=models.PROTECT )
  locator = models.CharField( max_length=100 )
  id_map = JSONField( blank=True ) # ie a dict of asset, chassis, system, etc types
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
  def state( self ):
    if self.located_at is None:
      return 'planned'

    elif self.located_at is not None and self.built_at is None:
      return 'located'

    return 'built'

  def __str__( self ):
    return 'Foundation #{0} of "{1}" in "{2}"'.format( self.pk, self.blueprint.pk, self.site.pk )


class Structure( models.Model ):
  hostname = models.CharField( max_length=100 )
  site = models.ForeignKey( Site, on_delete=models.PROTECT )           # ie where to build it
  blueprint = models.ForeignKey( StructureBluePrint, on_delete=models.PROTECT ) # ie what to bild
  foundation = models.ForeignKey( Foundation, on_delete=models.PROTECT )   # ie what to build it on
  config_values = JSONField( blank=True )
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

  class Meta:
    unique_together = ( ( 'site', 'hostname' ), )

  def clean( self, *args, **kwargs ): # verify hostname
    if not hostname_regex.match( self.hostname ):
      raise ValidationError( 'Structure hostname "{0}" is invalid'.format( self.name ) )

    super().clean( *args, **kwargs )

  def __str__( self ):
    return 'Instance #{0} of "{1}" in "{2}"'.format( self.pk, self.blueprint.pk, self.site.pk )

class Complex( models.Model ):
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

  def __str__( self ):
    return 'Complex "{0}"({1})'.format( self.description, self.name )
