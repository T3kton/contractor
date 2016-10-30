import json
import re

from django.db import models
from django.core.exceptions import ValidationError

name_regex = re.compile( '^[a-zA-Z0-9_\-]*$')
hostname_regex = re.compile( '^[a-zA-Z0-9_]*$' ) #TODO: get the real one

def validate_jsonfield( value ):
  if not isinstance( value, ( dict, list ) ):
    raise ValidationError( 'Value must be a python dict or dict, got %{type}', type=type( value ).__name__ )

def validate_list( value ):
  if not isinstance( value, list ):
    raise ValidationError( 'Value must be a python list, got %{type}', type=type( value ).__name__ )

class JSONField( models.TextField ):
  description = 'JSON Encoded'
  validators = [ validate_jsonfield ]
  #empty_values = [ None, '', [], {} ]

  def __init__( self, *args, **kwargs ):
    if 'default' not in kwargs:
      kwargs[ 'default' ] = {}

    if not isinstance( kwargs[ 'default' ], ( dict, list ) ):
      raise ValueError( 'deffult value must be a dict or list' )

    super().__init__( *args, **kwargs )

  def from_db_value( self, value, expression, connection, context ):
    if value is None:
      return value

    try:
      return json.loads( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

  def to_python( self, value ):
    if value is None:
      return value

    if isinstance( value, ( dict, list ) ):
      return value

    try:
      return json.loads( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

  def get_prep_value( self, value ):
    return json.dumps( value )


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
