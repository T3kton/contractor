from importlib import import_module

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from cinp.orm_django import DjangoCInP as CInP
from cinp.server_common import InvalidRequest

session_engine = import_module( settings.SESSION_ENGINE )


def getUser( auth_id, auth_token ):
  if auth_id is None or auth_token is None:
    return AnonymousUser()

  request = Request( session_engine.SessionStore( auth_token ) )

  if request.user.username != auth_id:
    return None

  if not request.user.is_active:
    return None

  return request.user


"""

TODO:
  add tracking logging, or some place to send tracking info
"""


class Request():
  def __init__( self, session, user=None ):
    self.session = session
    if user is None:
      self.user = auth.get_user( self )
    else:
      self.user = user
    self.user._django_session = session
    self.META = {}


cinp = CInP( 'Auth', '2.0' )


@cinp.staticModel( not_allowed_verb_list=[ 'LIST', 'GET', 'DELETE', 'CREATE', 'UPDATE' ] )
class User():
  @cinp.action( return_type='String', paramater_type_list=[ 'String', 'String' ] )
  @staticmethod
  def login( username, password ):
    user = auth.authenticate( username=username, password=password )
    if user is None:
      raise InvalidRequest( 'Invalid Login' )

    request = Request(session=session_engine.SessionStore( None ), user=user )

    auth.login( request, user )
    request.session.save()

    return request.session.session_key

  @cinp.action( paramater_type_list=[ '_USER_' ] )
  @staticmethod
  def logout( user ):
    request = Request( session=user._django_session, user=user )
    auth.logout( request )

  @cinp.action( return_type='String', paramater_type_list=[ '_USER_' ] )
  @staticmethod
  def whoami( user ):
    return str( user )

  @cinp.action( paramater_type_list=[ '_USER_', 'String' ] )
  @staticmethod
  def changePassword( user, password ):
    user.set_password( password )
    user.save()

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'User'
