import datetime
from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import name_regex, MapField
from contractor.Building.models import Foundation
from contractor.BluePrint.models import PXE
from contractor.Survey.lib import foundationLookup

cinp = CInP( 'Survey', '0.1' )


class SurveyException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'exception': 'SurveyException', 'error': self.code, 'message': self.message }

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
    return cinp.basic_auth_check( user, verb, Plot )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.name and not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if errors:
      raise ValidationError( errors )

  class Meta:
    pass
    # default_permissions = ( 'add', 'change', 'delete', 'view' )

  def __str__( self ):
    return 'Plot "{0}"({1})'.format( self.description, self.name )


@cinp.model( not_allowed_verb_list=[ 'CREATE', 'UPDATE' ] )
class Cartographer( models.Model ):
  identifier = models.CharField( max_length=64, primary_key=True )
  foundation = models.OneToOneField( Foundation, on_delete=models.PROTECT, null=True, blank=True )
  message = models.CharField( max_length=200 )
  info_map = MapField( null=True, blank=True )
  last_checkin = models.DateTimeField( null=True, blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  def _setFoundationPXE( self, done=False ):
    if done is True:
      pxe = None
    else:
      pxe = PXE.objects.get( name='bootstrap' )

    for iface in self.foundation.networkinterface_set.all():
      iface.pxe = pxe
      iface.full_clean()
      iface.save()

  @cinp.action( paramater_type_list=[ { 'type': 'Model', 'model': Foundation } ] )
  def assign( self, foundation ):
    if foundation.state != 'planned':
      raise SurveyException( 'FOUNDATION_INVALID_STATE', 'Foundation is not in a valid state for assigning' )

    self.foundation = foundation
    self.full_clean()
    self.save()

  @cinp.action( paramater_type_list=[ 'String' ] )
  @staticmethod
  def register( identifier ):
    try:
      locator = Cartographer.objects.get( identifier=identifier )
      locator.message = 'restarting'
      locator.full_clean()
      locator.save()
      return

    except Cartographer.DoesNotExist:
      pass

    locator = Cartographer()
    locator.identifier = identifier
    locator.message = 'new'
    locator.full_clean()
    locator.save()

  @cinp.action( return_type={ 'type': 'Map' }, paramater_type_list=[ 'Map' ] )
  def lookup( self, info_map=None ):
    self.info_map = info_map
    self.last_checkin = datetime.datetime.utcnow()
    self.full_clean()
    self.save()

    if self.foundation:
      self._setFoundationPXE()
      return { 'matched_by': 'Pre-Set', 'locator': self.foundation.locator }

    ( matched_by, foundation ) = foundationLookup( info_map )
    if foundation is not None:
      self.foundation = foundation
      self._setFoundationPXE()
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
    self._setFoundationPXE( done=True )
    foundation = self.foundation
    self.delete()
    foundation.cartographer = None  # the Cartographer instance is gone, but the object cache still has it, a little tweeking to help it get located
    foundation.refresh_from_db()
    foundation.setLocated()

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    if not cinp.basic_auth_check( user, verb, Cartographer ):
      return False

    if verb == 'CALL':
      if action in ( 'register', 'lookup', 'setMessage', 'done' ):
        return user.username == 'bootstrap'

      if action == 'assign':
        return user.has_perm( 'Survey.can_assign_foundation' )

    return True

  class Meta:
    default_permissions = ( 'delete', 'view' )
    permissions = (
                    ( 'can_assign_foundation', 'Can Assign Foundation to Cartographer' ),
                  )

  def __str__( self ):
    return 'Cartographer "{0}"'.format( self.identifier )
