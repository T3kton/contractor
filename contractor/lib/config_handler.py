import re
from cinp.server_common import Response, _fromPythonMap

from contractor.Building.models import Foundation, Structure
from contractor.Utilities.models import BaseAddress, NetworkInterface
from contractor.lib.config import getConfig, mergeValues, renderTemplate

url_regex = re.compile( '^/config/([a-z_]+)/((c/[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12})|(s/[0-9]+)|(f/[a-zA-Z0-9][a-zA-Z0-9_\-]*))?$' )


def handler( request ):
  match = url_regex.match( request.uri.lower() )
  if not match:
    return Response( 400, data='Invalid config uri', content_type='text' )

  ( request_type, _, config_uuid, structure_id, foundation_locator ) = match.groups()

  target = None
  interface = None

  if config_uuid is not None:
    try:
      target = Structure.objects.get( config_uuid=config_uuid[ 2: ] )
    except Structure.DoesNotExist:
      return Response( 404, data='Config UUID Not Found', content_type='text' )

    interface = target.provisioning_interface

  elif structure_id is not None:
    try:
      target = Structure.objects.get( pk=int( structure_id[ 2: ] ) )
    except Structure.DoesNotExist:
      return Response( 404, data='Structure Not Found', content_type='text' )

    interface = target.provisioning_interface

  elif foundation_locator is not None:
    try:
      target = Foundation.objects.get( pk=foundation_locator[ 2: ] )
    except Foundation.DoesNotExist:
      return Response( 404, data='Foundation Not Found', content_type='text' )

    interface = target.structure.provisioning_interface

  else:
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

    data = renderTemplate( template, config )
    return Response( 200, data=data, content_type='text' )

  elif request_type == 'config':
    _fromPythonMap( config )  # this does not go out CInP's converter, we need to make the python dict JSON encodable our selves
    return Response( 200, data=mergeValues( config ) )

  return Response( 400, data='Invalid request type', content_type='text' )
