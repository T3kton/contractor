import pickle

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import JSONField
from contractor.Site.models import Site
from contractor.Building.models import Foundation, Structure, Dependancy

# stuff for getting handeling tasks, everything here should be ephemerial, only things that are in progress/flight

cinp = CInP( 'Foreman', '0.1' )


@cinp.model( not_allowed_method_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', ) )
class BaseJob( models.Model ):
  JOB_STATE_CHOICES = ( ( 'queued', 'queued' ), ( 'waiting', 'waiting' ), ( 'done', 'done' ), ( 'paused', 'paused' ), ( 'error', 'error' ), ( 'aborted', 'aborted' ) )
  site = models.ForeignKey( Site, editable=False, on_delete=models.CASCADE )
  state = models.CharField( max_length=10, choices=JOB_STATE_CHOICES )
  status = JSONField( default=[], blank=True )
  message = models.CharField( max_length=1024, default='', blank=True )
  script_runner = models.BinaryField( editable=False )
  script_name = models.CharField( max_length=40, editable=False, default=False )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @property
  def realJob( self ):
    try:
      return self.foundationjob
    except ObjectDoesNotExist:
      pass

    try:
      return self.structurejob
    except ObjectDoesNotExist:
      pass

    try:
      return self.dependancyjob
    except ObjectDoesNotExist:
      pass

    return self

  def pause( self ):
    if self.state != 'queued':
      raise ValueError( 'Can only pause a job if it is queued' )

    self.state = 'paused'
    self.save()

  def resume( self ):
    if self.state != 'paused':
      raise ValueError( 'Can only resume a job if it is paused' )

    self.state = 'queued'
    self.save()

  def reset( self ):
    if self.state != 'error':
      raise ValueError( 'Can only reset a job if it is in error' )

    runner = pickle.loads( self.script_runner )
    runner.clearDispatched()
    self.status = runner.status
    self.script_runner = pickle.dumps( runner )

    self.state = 'queued'
    self.save()

  def rollback( self ):
    if self.state != 'error':
      raise ValueError( 'Can only rollback a job if it is in error' )

    runner = pickle.loads( self.script_runner )
    msg = runner.rollback()
    if msg != 'Done':
      raise ValueError( 'Unable to rollback "{0}"'.format( msg ) )

    self.status = runner.status
    self.script_runner = pickle.dumps( runner )
    self.state = 'queued'
    self.save()

  @property
  def progress( self ):
    try:
      return self.status[0][0]
    except IndexError:
      return 0.0

  @cinp.action( return_type={ 'type': 'Map' }, paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def jobStats( site ):
    return { 'running': BaseJob.objects.filter( site=site ).count(), 'error': BaseJob.objects.filter( site=site, state__in=( 'error', 'aborted', 'paused' ) ).count() }

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    if method == 'DESCRIBE':
      return True

    return False

  def clean( self, *args, **kwargs ):  # also need to make sure a Structure is in only one complex
    super().clean( *args, **kwargs )
    errors = {}

    if self.state not in self.JOB_STATE_CHOICES:
      errors[ 'state' ] = 'Invalid state "{0}"'.format( self.state )

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'BaseJob #{0} in "{1}"'.format( self.pk, self.site.pk )


@cinp.model( not_allowed_method_list=[ 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', 'status' ) )
class FoundationJob( BaseJob ):
  foundation = models.OneToOneField( Foundation, editable=False, on_delete=models.CASCADE )

  def done( self ):
    if self.script_name == 'destroy':
      self.foundation.setDestroyed()

    elif self.script_name == 'create':
      self.foundation.setBuilt()

  @cinp.action()
  def pause( self ):
    super().pause()

  @cinp.action()
  def resume( self ):
    super().resume()

  @cinp.action()
  def reset( self ):
    super().reset()

  @cinp.action()
  def rollback( self ):
    super().rollback()

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return FoundationJob.objects.filter( foundation__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'FoundationJob #{0} for "{1}" in "{2}"'.format( self.pk, self.foundation.pk, self.foundation.site.pk )


@cinp.model( not_allowed_method_list=[ 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', 'status' ) )
class StructureJob( BaseJob ):
  structure = models.OneToOneField( Structure, editable=False, on_delete=models.CASCADE )

  def done( self ):
    if self.script_name == 'destroy':
      self.structure.setDestroyed()

    elif self.script_name == 'create':
      self.structure.setBuilt()

  @property
  def foundation( self ):
    return self.structure.foundation

  @cinp.action()
  def pause( self ):
    super().pause()

  @cinp.action()
  def resume( self ):
    super().resume()

  @cinp.action()
  def reset( self ):
    super().reset()

  @cinp.action()
  def rollback( self ):
    super().rollback()

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return StructureJob.objects.filter( structure__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'StructureJob #{0} for "{1}" in "{2}"'.format( self.pk, self.structure.pk, self.structure.site.pk )


@cinp.model( not_allowed_method_list=[ 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', 'status' ) )
class DependancyJob( BaseJob ):
  dependancy = models.OneToOneField( Dependancy, editable=False, on_delete=models.CASCADE )

  def done( self ):
    self.dependancy.setBuilt()

  @cinp.action()
  def pause( self ):
    super().pause()

  @cinp.action()
  def resume( self ):
    super().resume()

  @cinp.action()
  def reset( self ):
    super().reset()

  @cinp.action()
  def rollback( self ):
    super().rollback()

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return DependancyJob.objects.filter( dependancy__foundation__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'DependancyJob #{0} for "{1}" in "{2}"'.format( self.pk, self.dependancy.pk, self.dependancy.structure.site.pk )
