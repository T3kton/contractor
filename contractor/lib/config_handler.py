import re
import json
from django.template import Template, Context
from cinp.server_common import Response

from contractor.Building.models import Foundation, Structure
from contractor.Utilities.models import NetworkInterface
from contractor.lib.config import getConfig


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
    interface = NetworkInterface.objects.get()
    target = interface.target

  if target is None or interface is None:
    return Response( 500, data='Target/Interface is missing', content_type='text' )

  data = None
  config = getConfig( target )

  if request_type == 'boot_script':
    template = Template( interface.pxe.boot_script )
    data = template.render( Context( config ) )
    return Response( 200, data=data, content_type='text;charset=utf-8' )

  elif request_type == 'pxe_template':
    template = Template( interface.pxe.pxe_template )
    data = template.render( Context( config ) )
    return Response( 200, data=data, content_type='text;charset=utf-8' )

  elif request_type == 'config':
    return Response( 200, data=json.dumps( data ), content_type='application/json;charset=utf-8' )

  return Response( 400, data='Invalid request type', content_type='text' )
