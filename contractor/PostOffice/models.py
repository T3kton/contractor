from datetime import datetime, timezone, timedelta

from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.Building.models import Foundation, Structure
from contractor.fields import MapField

MAX_BOX_LIFE = 96  # in hours
cinp = CInP( 'PostOffice', '0.1' )


class PostOfficeException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'class': 'PostOfficeException', 'error': self.code, 'message': self.message }

  def __str__( self ):
    return 'PostOfficeException ({0}): {1}'.format( self.code, self.message )


class Post( models.Model ):
  name = models.CharField( max_length=40 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  class Meta:
    abstract = True


@cinp.model( not_allowed_verb_list=[ 'CREATE', 'UPDATE', 'DELETE' ] )
class FoundationPost( Post ):
  foundation = models.ForeignKey( Foundation, on_delete=models.CASCADE, related_name='+' )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'FoundationPost for "{0}" on "{1}"'.format( self.foundation, self.name )


@cinp.model( not_allowed_verb_list=[ 'CREATE', 'UPDATE', 'DELETE' ] )
class StructurePost( Post ):
  structure = models.ForeignKey( Structure, on_delete=models.CASCADE, related_name='+' )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'StructurePost for "{0}" on "{1}"'.format( self.structure, self.name )


class Box( models.Model ):
  BOX_TYPE = ( ( 'post', 'POST' ), ( 'call', 'call (CINP)' ) )
  url = models.CharField( max_length=2048 )
  proxy = models.CharField( max_length=512, blank=True, null=True )
  type = models.CharField( max_length=4, choices=BOX_TYPE )
  one_shot = models.BooleanField( default=True )
  extra_data = MapField()
  expires = models.DateTimeField( blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def extend( self, additional_hours ):
    self.expires += timedelta( hour=additional_hours )
    self.full_clean()
    self.save()

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not self.expires:
      self.expires = None

    if not self.proxy:
      self.proxy = None

    errors = {}
    if self.expires is not None and not self.expires > datetime.now( timezone.utc ) + timedelta( hours=MAX_BOX_LIFE ):
      errors[ 'expires' ] = 'more than "{0}" hourse in the future'.format( MAX_BOX_LIFE )

    if not self.one_shot and self.exires is None:
      errors[ 'expires' ] = 'required when not one_shot'

    if errors:
      raise ValidationError( errors )

  class Meta:
    abstract = True


@cinp.model()
class FoundationBox( Box ):
  foundation = models.ForeignKey( Foundation, on_delete=models.CASCADE, related_name='+' )

  @cinp.action( paramater_type_list=[ 'Integer' ] )
  def extend( self, additional_hours ):
    super().extend( additional_hours )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'FoundationBox for "{0}"'.format( self.foundation )


@cinp.model()
class StructureBox( Box ):
  structure = models.ForeignKey( Structure, on_delete=models.CASCADE, related_name='+' )

  @cinp.action( paramater_type_list=[ 'Integer' ] )
  def extend( self, additional_hours ):
    super().extend( additional_hours )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'StructureBox for "{0}"'.format( self.structure )
