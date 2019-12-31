from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import name_regex
from contractor.Building.models import Foundation
from contractor.Survey.lib import foundationLookup

cinp = CInP( 'Survey', '0.1' )


class SurveyException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'class': 'SurveyException', 'error': self.code, 'message': self.message }

  def __str__( self ):
    return 'SurveyException ({0}): {1}'.format( self.code, self.message )


@cinp.model()
class Plot( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )
  corners = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', on_delete=models.PROTECT, null=True, blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.name and not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Plot "{0}"({1})'.format( self.description, self.name )


@cinp.model( not_allowed_verb_list=[ 'CREATE', 'UPDATE' ] )
class Cartographer( models.Model ):
  identifier = models.CharField( max_length=100, primary_key=True )
  foundation = models.OneToOneField( Foundation, on_delete=models.PROTECT, null=True, blank=True )
  message = models.CharField( max_length=200 )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.action( paramater_type_list=[ 'String' ] )
  @staticmethod
  def register( identifier ):
    try:
      Cartographer.objects.get( identifier=identifier )
      raise ValueError( 'Identifier "{0}" in use'.format( identifier ) )

    except Cartographer.DoesNotExist:
      pass

    locator = Cartographer()
    locator.identifier = identifier

    locator.full_clean()
    locator.save()

  @cinp.action( return_type={ 'type': 'Map' }, paramater_type_list=[ 'Map' ] )
  def lookup( self, info_map=None ):
    ( matched_by, foundation ) = foundationLookup( info_map )
    if foundation is not None:
      self.foundation = foundation
      self.message = 'Matched by "{0}" as "{1}"'.format( matched_by, foundation.locator )
      self.full_clean()
      self.save()

      return { 'matched_by': matched_by, 'locator': foundation.locator }

    return { 'matched_by': None }

  @cinp.action( paramater_type_list=[ 'String' ] )
  def setMessage( self, message ):
    self.message = message
    self.full_clean()
    self.save()

  @cinp.action()
  def done( self ):
    self.delete()
    self.foundation.setLocated()

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Cartographer "{0}"'.format( self.identifier )
