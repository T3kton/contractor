import pickle

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import JSONField
from contractor.Site.models import Site
from contractor.Building.models import Foundation, Structure, Dependancy

# stuff for getting handeling tasks, everything here should be ephemerial, only things that are in progress/flight

cinp = CInP( 'Foreman', '0.1' )


@cinp.model( not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', ) )
class BaseJob( models.Model ):
  JOB_STATE_CHOICES = ( 'queued', 'waiting', 'done', 'paused', 'error', 'aborted' )
  site = models.ForeignKey( Site, editable=False, on_delete=models.CASCADE )
  state = models.CharField( max_length=10, choices=[ ( i, i ) for i in JOB_STATE_CHOICES ] )
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
    self.full_clean()
    self.save()

  def resume( self ):
    if self.state != 'paused':
      raise ValueError( 'Can only resume a job if it is paused' )

    self.state = 'queued'
    self.full_clean()
    self.save()

  def reset( self ):
    if self.state != 'error':
      raise ValueError( 'Can only reset a job if it is in error' )

    runner = pickle.loads( self.script_runner )
    runner.clearDispatched()
    self.status = runner.status
    self.script_runner = pickle.dumps( runner )

    self.state = 'queued'
    self.full_clean()
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
    self.full_clean()
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

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerVariables( self ):
    result = {}
    runner = pickle.loads( self.script_runner )

    for module in runner.value_map:
      for name in runner.value_map[ module ]:
        result[ '{0}.{1}'.format( module, name ) ] = str( runner.value_map[ module ][ name ][0]() )

    result.update( runner.variable_map )

    return result

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerState( self ):
    result = {}
    runner = pickle.loads( self.script_runner )

    blueprint = None

    try:
      blueprint = self.foundationjob.foundation.blueprint
    except ObjectDoesNotExist:
      pass

    try:
      blueprint = self.structurejob.structure.blueprint
    except ObjectDoesNotExist:
      pass

    try:
      blueprint = self.dependancyjob.dependancy.blueprint
    except ObjectDoesNotExist:
      pass

    if blueprint is not None:
      result[ 'script' ] = blueprint.get_script( self.script_name )

    result[ 'cur_line' ] = runner.cur_line
    result[ 'state' ] = str( runner.state )

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if verb == 'DESCRIBE':
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


@cinp.model( not_allowed_verb_list=[ 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', ) )
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

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerVariables( self ):
    return super().jobRunnerVariables()

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerState( self ):
    return super().jobRunnerState()

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return FoundationJob.objects.filter( foundation__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'FoundationJob #{0} for "{1}" in "{2}"'.format( self.pk, self.foundation.pk, self.foundation.site.pk )


@cinp.model( not_allowed_verb_list=[ 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', ) )
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

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerVariables( self ):
    return super().jobRunnerVariables()

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerState( self ):
    return super().jobRunnerState()

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return StructureJob.objects.filter( structure__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'StructureJob #{0} for "{1}" in "{2}"'.format( self.pk, self.structure.pk, self.structure.site.pk )


@cinp.model( not_allowed_verb_list=[ 'CREATE', 'UPDATE', 'DELETE' ], hide_field_list=( 'script_runner', ), property_list=( 'progress', ) )
class DependancyJob( BaseJob ):
  dependancy = models.OneToOneField( Dependancy, editable=False, on_delete=models.CASCADE )

  def done( self ):
    if self.script_name == self.dependancy.destroy_script_name:
      self.dependancy.setDestroyed()

    elif self.script_name == self.dependancy.create_script_name:
      self.dependancy.setBuilt()

    else:
      raise ValueError( 'Sciprt Name "{0}" does not match the create nor destroy script names' )  # Dependancy jobs can only create/destory, not named/utility sjobs

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

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerVariables( self ):
    return super().jobRunnerVariables()

  @cinp.action( return_type={ 'type': 'Map' } )
  def jobRunnerState( self ):
    return super().jobRunnerState()

  @cinp.list_filter( name='site', paramater_type_list=[ { 'type': 'Model', 'model': 'contractor.Site.models.Site' } ] )
  @staticmethod
  def filter_site( site ):
    return DependancyJob.objects.filter( dependancy__foundation__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'DependancyJob #{0} for "{1}" in "{2}"'.format( self.pk, self.dependancy.pk, self.dependancy.structure.site.pk )
