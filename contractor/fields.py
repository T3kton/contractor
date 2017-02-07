import json
import re

from django.db import models
from django.core.exceptions import ValidationError

name_regex = re.compile( '^[a-zA-Z0-9_\-]*$')
hostname_regex = re.compile( '^[a-zA-Z0-9_]*$' ) #TODO: get the real one

def validate_mapfield( value ):
  if not isinstance( value, dict):
    raise ValidationError( 'Value must be a python dict, got %{type}', type=type( value ).__name__ )

def validate_list( value ):
  if not isinstance( value, list ):
    raise ValidationError( 'Value must be a python list, got %{type}', type=type( value ).__name__ )

class MapField( models.TextField ):
  description = 'JSON Encoded Map'
  validators = [ validate_mapfield ]
  cinp_type = 'Map'
  #empty_values = [ None, '', [], {} ]

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

  def value_to_string( self, obj ):
    return json.dumps( self._get_val_from_obj( obj ) )


class StringListField( models.CharField ):
  description = 'String List'
  validators = [ validate_list ]

  def __init__( self, *args, **kwargs ):
    if 'default' not in kwargs:
      kwargs[ 'default' ] = []
    if 'null' in kwargs: # the field needs to be valid JSON, None is not valid
      del kwargs[ 'null' ]

    if not isinstance( kwargs[ 'default' ], list ):
      raise ValueError( 'default value must be a list' )

    super().__init__( *args, **kwargs )

  def from_db_value( self, value, expression, connection, context ):
    if value is None:
      return value

    return value.split( '\t' )

  def to_python( self, value ):
    if value is None:
      return value

    if isinstance( value, list ):
      return value

    return value.split( '\t' )

  def get_prep_value( self, value ):
    return '\t'.join( value )
