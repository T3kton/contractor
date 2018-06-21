import json
import re

from django.db import models
from django.core.exceptions import ValidationError

from contractor.lib.ip import StrToIp, IpToStr

name_regex = re.compile( '^[a-zA-Z0-9][a-zA-Z0-9_\-]*$' )  # if  this changes, update architect
hostname_regex = re.compile( '^[a-z0-9][a-z0-9\-]*[a-z0-9]$' )  # '.' is not allowed, can cause trouble with the DNS generations stuff, must also be lowercase (DNS is non case sensitive)
config_name_regex = re.compile( '^[{}\-~]?([a-zA-Z0-9]+:)?[a-zA-Z0-9][a-zA-Z0-9_\-]*$' )
JSON_MAGIC = '\x02JSON\x03'


def validate_mapfield( value ):
  if not isinstance( value, dict ):
    raise ValidationError( 'Value must be a python dict, got %(type)s', params={ 'type': type( value ).__name__ } )


def validate_list( value ):
  if not isinstance( value, list ):
    raise ValidationError( 'Value must be a python list, got %(type)s', params={ 'type': type( value ).__name__ } )


def validate_ipaddress( value ):
  try:
    StrToIp( value )
  except ValueError:
    raise ValidationError( 'Invalid Ip Address "%(value)s"', params={ 'value': value[ 0:100 ] } )


class MapField( models.TextField ):
  description = 'JSON Encoded Map'
  validators = [ validate_mapfield ]
  cinp_type = 'Map'

  def __init__( self, *args, **kwargs ):
    if 'default' not in kwargs:
      kwargs[ 'default' ] = {}

    if not isinstance( kwargs[ 'default' ], dict ):
      raise ValueError( 'default value must be a dict' )

    super().__init__( *args, **kwargs )

  def from_db_value( self, value, expression, connection, context ):
    if value is None or value == '':
      return None

    try:
      value = json.loads( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

    if value is not None and not isinstance( value, dict ):
      raise ValidationError( 'DB Stored JSON does not encode a dict' )

    return value

  def to_python( self, value ):
    if value is None:
      return None

    if isinstance( value, dict ):
      return value

    try:
      value = json.loads( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

    if value is not None and not isinstance( value, dict ):
      raise ValidationError( 'Value in JSON does not encode a dict' )

    return value

  def get_prep_value( self, value ):
    if not isinstance( value, dict ):
      raise ValidationError( 'value is not a dict' )

    return json.dumps( value )


class JSONField( models.TextField ):
  description = 'JSON Encoded'

  def from_db_value( self, value, expression, connection, context ):
    if value is None or value == '':
      return None

    try:
      value = json.loads( value[ len( JSON_MAGIC ): ] )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

    return value

  def to_python( self, value ):
    if value is None:
      return None

    if not isinstance( value, str ) or not value.startswith( JSON_MAGIC ):
      return value

    try:
      value = json.loads( value[ len( JSON_MAGIC ): ] )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

    if value is not None and not isinstance( value, dict ):
      raise ValidationError( 'Value in JSON does not encode a dict' )

    return value

  def get_prep_value( self, value ):
    return JSON_MAGIC + json.dumps( value )


class StringListField( models.CharField ):
  description = 'String List'
  validators = [ validate_list ]

  def __init__( self, *args, **kwargs ):
    if 'default' not in kwargs:
      kwargs[ 'default' ] = []
    try:
      del kwargs[ 'null' ]
    except KeyError:
      pass

    if not isinstance( kwargs[ 'default' ], list ):
      raise ValueError( 'default value must be a list' )

    super().__init__( *args, **kwargs )

  def from_db_value( self, value, expression, connection, context ):
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


class IpAddressField( models.IntegerField ):
  description = 'Ip Address Field'
  validators = [ validate_ipaddress ]
  cinp_type = 'String'

  def from_db_value( self, value, expression, connection, context ):
    if value is None:
      return None

    try:
      return IpToStr( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid', params={ 'value': value } )

  def to_python( self, value ):
    if value is None:
      return None

    if isinstance( value, str ):
      return value

    try:
      return IpToStr( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid', params={ 'value': value } )

  def get_prep_value( self, value ):
    return StrToIp( value )

  def value_to_string( self, obj ):
    return self.get_prep_value( self._get_val_from_obj( obj ) )
