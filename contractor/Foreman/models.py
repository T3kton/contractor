from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import JSONField
from contractor.Site.models import Site
from contractor.Building.models import Foundation, Structure

# stuff for getting handeling tasks, everything here should be ephemerial, only things that are in progress/flight

cinp = CInP( 'Foreman', '0.1' )


@cinp.model( not_allowed_method_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE', 'CALL' ], hide_field_list=( 'script_pos', 'script_ast' ) )
class BaseJob( models.Model ): # abstract base class
  JOB_STATE_CHOICES = ( ( 'working', 'working' ), ( 'waiting', 'waiting' ), ( 'done', 'done' ), ( 'pause', 'pause' ), ( 'error', 'error' ) )
  site = models.ForeignKey( Site, editable=False, on_delete=models.CASCADE )
  state = models.CharField( max_length=10, choices=JOB_STATE_CHOICES )
  script_pos = JSONField( editable=False, default={} )
  script_ast = JSONField( editable=False, default={} )
  is_create = models.BooleanField( editable=False, default=False ) # if it is neither create nor destroy, it is utility
  is_destroy = models.BooleanField( editable=False, default=False )
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

    return self

  def pause( self ):
    if self.state != 'working':
      raise ValueError( 'Can only pause a job if it is working' )

    self.state = 'pause'
    self.save()

  def clean( self, *args, **kwargs ): # also need to make sure a Structure is in only one complex
    super().clean( *args, **kwargs )
    errors = {}
    if self.is_create and self.is_destroy:
      errors[ 'is_create' ] = 'Can not be a create and a destroy script at the same time'
      errors[ 'is_destroy' ] = 'Can not be a create and a destroy script at the same time'

    if self.state not in JOB_STATE_CHOICES:
      errors[ 'state' ] = 'Invalid state "{0}"'.format( self.state )

    if errors:
      raise ValidationError( errors )


  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    if method == 'DESCRIBE':
      return True

    return False

  def __str__( self ):
    return 'BaseJob #{0} in "{1}"'.format( self.pk, self.site.pk)


@cinp.model( not_allowed_method_list=[ 'CREATE', 'UPDATE', 'DELETE', 'CALL' ] )
class FoundationJob( BaseJob ):
  foundation = models.OneToOneField( Foundation, editable=False, on_delete=models.CASCADE )

  def done( self ):
    if self.is_destroy:
      self.foundation.setDestroyed()
    elif self.is_create:
      self.foundation.setBuilt()

  @cinp.list_filter( name='site', paramater_type_list=[ 'Model:contractor.Site.models.Site' ] )
  @staticmethod
  def filter_site( site ):
    return FoundationJob.objects.filter( foundation__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'FoundationJob #{0} for "{1}" in "{2}"'.format( self.pk, self.foundation.pk, self.foundation.site.pk )


@cinp.model( not_allowed_method_list=[ 'CREATE', 'UPDATE', 'DELETE', 'CALL' ] )
class StructureJob( BaseJob ):
  structure = models.OneToOneField( Structure, editable=False, on_delete=models.CASCADE )

  def done( self ):
    if self.is_destroy:
      self.structure.setDestroyed()
    elif self.is_create:
      self.structure.setBuilt()

  @cinp.list_filter( name='site', paramater_type_list=[ 'Model:contractor.Site.models.Site' ] )
  @staticmethod
  def filter_site( site ):
    return StructureJob.objects.filter( structure__site=site )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'StructureJob #{0} for "{1}" in "{2}"'.format( self.pk, self.structure.pk, self.structure.site.pk )
