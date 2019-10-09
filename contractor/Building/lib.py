# from contractor.Building.models import Structure
from contractor.Utilities.models import NetworkInterface, Address


def structureLookup( info_map ):  # TODO: do we bail when what we come to failes? or do we keep going, or a paramater that saies to keep trying, and/or a list of all the possibilities
  # if 'config_uuid' in info_map:
  #   try:
  #     return Structure.objects.get( config_uuid=info_map[ 'config_uuid' ] )
  #   except Structure.DoesNotExist:
  #     return None

  if 'lldp' in info_map:
    iface_list = NetworkInterface.objects.filter( link_name=info_map[ 'lldp' ] )
    if len( iface_list ) > 1:
      raise Exception( 'To Many results' )

    return iface_list[0].foundation.structure

  if 'ip_address' in info_map:
    address = Address.lookup( info_map[ 'ip_address' ] )
    return address.structure

  return None
