import re
import pickle
from jinja2 import Template
from cinp.server_common import Response

from contractor.Building.models import Foundation, Structure
from contractor.Utilities.models import BaseAddress, NetworkInterface
from contractor.lib.config import getConfig


def _dictConverter( value ):
  _fromPythonMap( value )
  return value

MAP_TYPE_CONVERTER = {
                       'NoneType': lambda a: None,
                       'str': str,
                       'int': str,
                       'float': str,
                       'bool': str,
                       'datetime': lambda a: a.isoformat(),
                       'timedelta': lambda a: a.total_seconds(),
                       'dict': _dictConverter
                     }


def _fromPythonMap_converter( value ):
  try:
    return MAP_TYPE_CONVERTER[ type( value ).__name__ ]( value )
  except KeyError:
    raise ValueError( 'no converter for type "{0}" in map converter'.format( type( value ).__name__ ) )


def _fromPythonMap( value ):
  for key in value.keys():
    if isinstance( value[ key ], tuple ):  # convert tuple to list before iterating
      value[ key ] = list( value[ key ] )

    if isinstance( value[ key ], dict ):
      _fromPythonMap( value[ key ] )

    elif isinstance( value[ key ], list ):
      for index in range( 0, len( value[ key ] ) ):
        value[ key ][ index ] = _fromPythonMap_converter( value[ key ][ index ] )

    else:
      value[ key ] = _fromPythonMap_converter( value[ key ] )


def _mergeConfig( template, values ):
  while template.count( '{{' ):
    tpl = Template( template )
    template = tpl.render( **values )

  return template


def handler( request ):
  if not re.match( '^/config/[a-z_]+/([sf][0-9]+)?$', request.uri ):
    return Response( 400, data='Invalid config uri', content_type='text' )

  ( _, _, request_type, target_id ) = request.uri.split( '/' )

  target = None
  interface = None

  if len( target_id ) > 0:
    if target_id[0] == 's':
      try:
        target = Structure.objects.get( pk=int( target_id[ 1: ] ) )
      except Structure.DoesNotExist:
        return Response( 404, data='Structure Not Found', content_type='text' )

    elif target_id[0] == 'f':
      try:
        target = Foundation.objects.get( pk=int( target_id[ 1: ] ) )
      except Foundation.DoesNotExist:
        return Response( 404, data='Foundation Not Found', content_type='text' )

    else:
      return Response( 500, data='Target Confusion', content_type='text' )

    interface = target.provisioning_interface

  else:
    print( 'Getting config goodies for "{0}"'.format( request.remote_addr ) )
    address = BaseAddress.lookup( request.remote_addr )
    if address is None:
      return Response( 404, data='Address Not Found', content_type='text' )

    address = address.subclass
    if address.type != 'Address':
      return Response( 404, data='Address Not Valid', content_type='text' )

    target = address.networked.subclass
    try:
      if isinstance( target, Structure ):
        interface = target.foundation.networkinterface_set.get( name=address.interface_name )
      else:
        interface = target.networkinterface_set.get( name=address.interface_name )

    except NetworkInterface.DoesNotExist:
      return Response( 404, data='Interface Not Found', content_type='text' )

  if target is None or interface is None:
    return Response( 500, data='Target/Interface is missing', content_type='text' )

  data = None
  config = getConfig( target )

  if request_type in ( 'boot_script', 'pxe_template' ):
    pxe = interface.pxe
    if pxe is None:
      return Response( 200, data='', content_type='text' )

    if request_type == 'boot_script':
      template = '#!ipxe\n\n' + pxe.boot_script

    elif request_type == 'pxe_template':
      template = pxe.template

    data = _mergeConfig( template, config )
    print( 'config_handler sending "{0}" to "{1}"\n    -----------    '.format( request_type, request.remote_addr ) )
    print( data )
    print( '    -----------    ')
    return Response( 200, data=data, content_type='text' )

  elif request_type == 'config':
    _fromPythonMap( config )
    template = pickle.dumps( config, 0 ).decode()  # Yeah, there is probably a better way to merge values in.
    return Response( 200, data=pickle.loads( _mergeConfig( template, config ).encode() ) )

  return Response( 400, data='Invalid request type', content_type='text' )
