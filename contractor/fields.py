import json
import pickle
import re

from django.db import models
from django.core.exceptions import ValidationError

from contractor.lib.ip import StrToIp, IpToStr

name_regex = re.compile( r'^[a-zA-Z0-9][a-zA-Z0-9_\-]*$' )  # if this changes, update architect, and config_handler uri regex
hostname_regex = re.compile( r'^[a-z0-9][a-z0-9\-]*[a-z0-9]$' )  # '.' is not allowed, can cause trouble with the DNS generations stuff, must also be lowercase (DNS is non case sensitive)
config_name_regex = re.compile( r'^[<>\-~]?[a-zA-Z0-9][a-zA-Z0-9_\-]*(:[a-zA-Z0-9]+)?$' )
JSON_MAGIC = '\x02JSON\x03'


def validate_list( value ):
  if not isinstance( value, list ):
    raise ValidationError( 'Value must be a python list, got %(type)s', params={ 'type': type( value ).__name__ } )


def validate_ipaddress( value ):
  try:
    StrToIp( value )
  except ValueError:
    raise ValidationError( 'Invalid Ip Address "%(value)s"', params={ 'value': value[ 0:100 ] } )


def defaultdict():
  return dict()


class MapField( models.BinaryField ):
  description = 'Map Field'
  cinp_type = 'Map'
  empty_values = [ None, {} ]

  def __init__( self, *args, **kwargs ):
    if 'default' in kwargs:
      default = kwargs[ 'default' ]
      if kwargs.get( 'null', False ) and default is None:
        pass

      elif not callable( default ) and not isinstance( default, dict ):
        raise ValueError( 'default value must be a dict or callable.' )

    else:
      kwargs[ 'default' ] = defaultdict

    editable = kwargs.get( 'editable', True )
    super().__init__( *args, **kwargs )  # until Django 2.1, editable for BinaryFields is not able to be made editable
    self.editable = editable

  def deconstruct( self ):
    editable = self.editable
    self.editable = False  # have to set this to non default so BinaryField's deconstruct works
    name, path, args, kwargs = super( MapField, self ).deconstruct()
    self.editable = editable
    kwargs[ 'editable' ] = self.editable
    return name, path, args, kwargs

  def from_db_value( self, value, expression, connection, context=None ):  # remove context when moving to Focal
    if value is None:
      return None

    try:
      value = pickle.loads( value )
    except ValueError:
      raise ValidationError( 'DB Value is not a valid Pickle.', code='invalid' )

    if value is not None and not isinstance( value, dict ):
      raise ValidationError( 'DB Stored Value does not encode a dict.', code='invalid' )

    return value

  def to_python( self, value ):
    if value is None and self.null:
      return None

    if isinstance( value, dict ):
      return value

    raise ValidationError( 'must be a dict.', code='invalid'  )

  def get_prep_value( self, value ):
    if value is None:
      return None

    if not isinstance( value, dict ):
      raise ValidationError( 'value is not a dict.', code='invalid'  )

    return pickle.dumps( value, protocol=4 )


class JSONField( models.TextField ):
  description = 'JSON Encoded'
  empty_values = [ None ]

  def from_db_value( self, value, expression, connection, context=None ):  # remove context when moving to Focal
    if value is None:
      return None

    try:
      value = json.loads( value[ len( JSON_MAGIC ): ] )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

    return value

  def to_python( self, value ):
    if value is None:
      return None

    if isinstance( value, str ) and value.startswith( JSON_MAGIC ):
      return json.loads( value[ len( JSON_MAGIC ): ] )

    else:
      return value

  def get_prep_value( self, value ):
    if value is None:
      return None

    return JSON_MAGIC + json.dumps( value )


class StringListField( models.CharField ):
  description = 'String List'
  validators = [ validate_list ]
  cinp_is_array = True

  def __init__( self, *args, **kwargs ):
    if 'max_length' not in kwargs:
      raise ValueError( '"max_length" is required' )

    if 'default' not in kwargs:
      kwargs[ 'default' ] = list

    else:
      if not callable( kwargs[ 'default' ] ) and not isinstance( kwargs[ 'default' ], list ):
        raise ValueError( 'default value must be a list' )

    try:
      del kwargs[ 'null' ]  # can not be default = None either
    except KeyError:
      pass

    super().__init__( *args, **kwargs )

  def from_db_value( self, value, expression, connection, context=None ):  # remove context when moving to Focal
    if value is None:
      return value

    if value == '':
      return []

    return value.split( '\t' )

  def to_python( self, value ):
    if value is None:
      return value

    if isinstance( value, list ):
      return value

    if value == '':
      return []

    return value.split( '\t' )

  def get_prep_value( self, value ):
    return '\t'.join( value )


class IpAddressField( models.BinaryField ):  # needs 128 bits of storage, the integer types only goto 64
  description = 'Ip Address Field'
  validators = [ validate_ipaddress ]
  cinp_type = 'String'

  def __init__( self, *args, **kwargs ):
    if 'default' in kwargs:
      default = kwargs[ 'default' ]

      if kwargs.get( 'null', False ) and default is None:
        pass

      elif not callable( default ) and not isinstance( default, str ):
        raise ValueError( 'default value must be a str or callable.' )

      elif not callable( default ):
        try:
          validate_ipaddress( default )
        except ValidationError:
          raise ValueError( 'invalid default value' )

    editable = kwargs.get( 'editable', True )
    super().__init__( *args, **kwargs )  # until Django 2.1, editable for BinaryFields is not able to be made editable
    self.editable = editable

  def deconstruct( self ):
    editable = self.editable
    self.editable = False  # have to set this to non default so BinaryField's deconstruct works
    name, path, args, kwargs = super( IpAddressField, self ).deconstruct()
    self.editable = editable
    kwargs[ 'editable' ] = self.editable
    return name, path, args, kwargs

  def from_db_value( self, value, expression, connection, context=None ):  # remove context when moving to Focal
    if value is None:
      return None

    try:
      return IpToStr( int.from_bytes( value, 'big' ) )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid', params={ 'value': value } )

  def to_python( self, value ):
    if value is None:
      return None

    if isinstance( value, str ):
      return value

    if isinstance( value, int ):
      try:
        return IpToStr( value )
      except ValueError:
        raise ValidationError( '"%(value)s" is not valid', params={ 'value': value } )

    if isinstance( value, bytes ):
      try:
        return IpToStr( int.from_bytes( value, 'big' ) )
      except ValueError:
        raise ValidationError( '"%(value)s" is not valid', params={ 'value': value } )

    raise ValidationError( '"%(value)s" type is unexpected type "%(type)s"', params={ 'value': value, 'type': type } )

  def get_prep_value( self, value ):
    if isinstance( value, str ):
      value = StrToIp( value )

    if value is None:  # StrToIp may return None
      return None

    return value.to_bytes( 16, 'big' )

  def value_to_string( self, obj ):
    return self.get_prep_value( self._get_val_from_obj( obj ) )
