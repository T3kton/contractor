from contractor.Building.models import Structure
from contractor.Utilities.models import RealNetworkInterface, BaseAddress


def foundationLookup( info_map ):
  # find the first thing that matches, blueprint.validateIdMap will verify the hardware and disks, what is going to validate LLDP?

  # first we check if we are spicifically assigned via something manual or network pinning
  if 'config_uuid' in info_map:
    try:
      structure = Structure.objects.get( config_uuid=info_map[ 'config_uuid' ] )
      return ( 'configu_uuid', structure.foundation )
    except Structure.DoesNotExist:
      return ( None, None )

  # next via LLDP, there is little to enfoce DMI information uniqueness
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

  # next up, mabey we have a pre-defined ip address
  if 'ip_address' in info_map:  # NOTE: BaseAddress returns None if ip_address is duplicate
    address = BaseAddress.lookup( info_map[ 'ip_address' ] ).subclass
    if address.type == 'Address':
      return ( 'ip_address: "{0}"'.format( info_map[ 'ip_address' ] ), address.structure.foundation )

  # lastely DMI/Hardware information
  if 'hardware' in info_map:
    # look up hardware by info_map[ 'hardware' ][ 'dmi' ][ 'Base Board Information' ][ 'Product Name' or 'Serial Number' or 'Asset Tag' ]
    pass

  return ( None, None )
