import re
from contractor.Utilities.models import RealNetworkInterface, BaseAddress


def foundationLookup( info_map ):  # TODO: do we bail when what we come to failes? or do we keep going, or a paramater that saies to keep trying, and/or a list of all the possibilities
  # if 'config_uuid' in info_map:
  #   try:
  #     return Structure.objects.get( config_uuid=info_map[ 'config_uuid' ] )
  #   except Structure.DoesNotExist:
  #     return None

  if 'hardware' in info_map:
    # look up hardware by info_map[ 'hardware' ][ 'dmi' ][ 'Base Board Information' ][ 'Product Name' or 'Serial Number' or 'Asset Tag' ]
    pass

  if 'lldp' in info_map:
    for iface_name, lldp_info in info_map[ 'lldp' ].items():
      lldp_name = '{0}-{1}-{2}-{3}'.format( lldp_info[ 'mac' ], lldp_info[ 'slot' ], lldp_info[ 'port' ], lldp_info[ 'subport' ] )
      try:
        iface = RealNetworkInterface.objects.get( link_name=lldp_name )
        return ( 'lldp by mac interface: "{0}"'.format( iface_name ), iface.foundation )
      except ( RealNetworkInterface.MultipleObjectsReturned, RealNetworkInterface.DoesNotExist ):
        pass

      lldp_name = '{0}-{1}-{2}-{3}'.format( lldp_info[ 'name' ], lldp_info[ 'slot' ], lldp_info[ 'port' ], lldp_info[ 'subport' ] )
      try:
        iface = RealNetworkInterface.objects.get( link_name=lldp_name )
        return ( 'lldp by name interface: "{0}"'.format( iface_name ), iface.foundation )
      except ( RealNetworkInterface.MultipleObjectsReturned, RealNetworkInterface.DoesNotExist ):
        pass

  if 'ip_address' in info_map:
    address = BaseAddress.lookup( info_map[ 'ip_address' ] ).subclass
    if address.type == 'Address':
      return ( 'ip_address: "{0}"'.format( info_map[ 'ip_address' ] ), address.structure.foundation )

  return ( None, None )


def validateTemplate( id_map, item_map ):  # return message as a string if something does not match
  for name in item_map:
    try:
      value = id_map[ name.split( '.' ) ]
    except KeyError:
      return 'Item "{0}" not found'.format( name )

    if not re.match( id_map[ name ], value ):
      return 'Item "{0}" does not match "{1}"'.format( name, id_map[ name ] )

  return None
