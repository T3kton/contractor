import os

from django.conf import settings

from contractor.lib.ip import IpIsV4
from contractor.Utilities.models import Networked
from contractor.Directory.models import Entry

TEMPLATES = {}
TEMPLATES[ 'SOA' ] = """$TTL {ttl}
$ORIGIN {zone}.
@  IN SOA {master}. {email}. (
            **ZONE_SERIAL**
            {refresh}
            {retry}
            {expire}
            {minimum}
          )
"""
TEMPLATES[ 'NS' ] = '{name:<50} IN NS    {server}.'
TEMPLATES[ 'MX' ] = '{name:<50} IN MX    {priority:>4} {target}'
TEMPLATES[ 'A' ] = '{name:<50} IN A     {address}'
TEMPLATES[ 'AAAA' ] = '{name:<50} IN AAAA  {address}'
TEMPLATES[ 'PTR' ] = '{value:<50} IN PTR   {target}'
TEMPLATES[ 'CNAME' ] = '{name:<50} IN CNAME {target}'
TEMPLATES[ 'TXT' ] = '{name:<50} IN TXT   "{target}"'
TEMPLATES[ 'RTXT' ] = '{value:<50} IN TXT   "{target}"'
TEMPLATES[ 'SRV' ] = '{name:<50} IN SRV   {priority:>4} {weight:>4} {port:>5} {target}'
TEMPLATES[ 'SIG' ] = '{name:<50} IN SIG   {sig}'

MASTER_NS_NETWORKED = Networked.objects.get( pk=settings.BIND_NS_NETWORKED_LIST[0] )
MASTER_NS_HOSTNAME = '{0}.{1}'.format( MASTER_NS_NETWORKED.primary_interface.name, MASTER_NS_NETWORKED.fqdn )
REVERSE_SOA = { 'ttl': 3600,
                'refresh': 86400,
                'retry': 7200,
                'expire': 36000,
                'minimum': 172800,
                'master': MASTER_NS_HOSTNAME,
                'email': settings.BIND_SOA_EMAIL
                }


def _render( rec_type, parms ):
  if isinstance( parms, list ):
    return ''.join( [ _render( rec_type, i ) for i in parms ] )

  try:
    template = TEMPLATES[ rec_type ]
  except KeyError:
    raise ValueError( 'Invalid Record Type "{0}"'.format( rec_type ) )

  return template.format( **parms ) + '\n'


def _getNetworkedEntries( networked, site_list ):
  networked = networked.subclass
  result = { 'RTXT': [], 'PTR': [], 'TXT': [], 'A': [], 'CNAME': [] }

  for address in networked.address_set.all():
    address_block = address.address_block
    if address_block.site not in site_list:
      continue

    iface = address.interface
    if not iface:
      continue
    nab = address_block.networkaddressblock_set.get( network=iface.network )
    ip_addr = networked.primary_address.ip_address

    full_name = iface.name

    if address.alias_index is not None:
      full_name = '{0}-{1}'.format( full_name, address.alias_index )

    if nab.vlan:
      full_name = 'v{0}.{1}'.format( nab.vlan, full_name )

    result[ 'RTXT' ].append( { 'value': ip_addr, 'target': '{0}.{1}'.format( full_name, networked.fqdn ) } )
    result[ 'PTR' ].append( { 'value': ip_addr, 'target': networked.fqdn } )
    result[ 'TXT' ].append( { 'name': '{0}.{1}'.format( full_name, networked.hostname ), 'target': networked.foundation.locator } )
    if IpIsV4( ip_addr ):
      result[ 'A' ].append( { 'name': '{0}.{1}'.format( full_name, networked.hostname ), 'address': ip_addr } )
    else:
      result[ 'AAAA' ].append( { 'name': '{0}.{1}'.format( full_name, networked.hostname ), 'address': ip_addr } )
    if address.is_primary:
      result[ 'CNAME' ].append( { 'name': networked.hostname, 'target': '{0}.{1}'.format( full_name, networked.hostname ) } )

  return result


def genZone( zone, ptr_list, rtext_list, zone_file_list ):
  record_map = {}
  for rec_type in TEMPLATES.keys():
    record_map[ rec_type ] = []

  zone_fqdn = zone.fqdn
  site_list = list( zone.site_set.all() )

  for ns in settings.BIND_NS_NETWORKED_LIST:
    networked = Networked.objects.get( pk=ns )
    hostname = '{0}.{1}'.format( networked.primary_interface.name, networked.fqdn )
    record_map[ 'NS' ].append( { 'name': '@', 'server': hostname } )
    if networked.site not in site_list and hostname.endswith( zone_fqdn ):  # Add a glue record, when the server is not in this zone file AND in a parent of the zone it belonds too
      record_map[ 'A' ].append( { 'name': hostname + '.', 'address': networked.primary_address.address.ip_address } )

  for site in site_list:
    for networked in site.networked_set.all():
      entry_list = _getNetworkedEntries( networked, site_list )
      for entry_type in entry_list.keys():
        record_map[ entry_type ] += entry_list[ entry_type ]

  for entry in zone.entry_set.all():
    record_map[ entry.type ].append( {
                                       'name': entry.name,
                                       'priority': entry.priority,
                                       'weight': entry.weight,
                                       'port': entry.port,
                                       'target': entry.target
                                     } )

  existing_names = [ i[ 'name' ] for i in ( record_map[ 'A' ] + record_map[ 'AAAA' ] + record_map[ 'CNAME' ] ) ]
  for entry in Entry.objects.filter( zone__isnull=True ):
    if entry.type == 'CNAME' and entry.name in existing_names:
      continue

    record_map[ entry.type ].append( {
                                       'name': entry.name,
                                       'priority': entry.priority,
                                       'weight': entry.weight,
                                       'port': entry.port,
                                       'target': entry.target
                                     } )

  record_map[ 'SOA' ] = [ {
                            'zone': zone_fqdn,
                            'master': MASTER_NS_HOSTNAME,
                            'ttl': zone.ttl,
                            'email': settings.BIND_SOA_EMAIL,
                            'refresh': zone.refresh,
                            'retry': zone.retry,
                            'expire': zone.expire,
                            'minimum': zone.minimum
                          } ]

  ptr_list += record_map[ 'PTR' ]
  rtext_list += record_map[ 'RTXT' ]

  del record_map[ 'PTR' ]
  del record_map[ 'RTXT' ]

  result = ''
  for rec_type in ( 'SOA', 'NS', 'SIG', 'SRV', 'A', 'AAAA', 'CNAME', 'TXT' ):
    result += _render( rec_type, record_map[ rec_type ] )  # TODO: Sort record map, and get rid of duplicates

  filename = '{0}.zone'.format( zone_fqdn )

  zone_file_list.append( ( filename, zone_fqdn ) )

  return filename, result


def genPtrZones( ptr_list, rtext_list, zone_file_list ):
  zone_ptr_map = {}
  zone_rtxt_map = {}

  for ptr in ptr_list:
    parts = ptr[ 'value' ].split( '.' )
    zone = '.'.join( reversed( parts[ :3 ] ) ) + '.in-addr.arpa'
    try:
      zone_ptr_map[ zone ].append( { 'value': parts[3], 'target': ptr[ 'target' ] + '.' } )
    except KeyError:
      zone_ptr_map[ zone ] = [ { 'value': parts[3], 'target': ptr[ 'target' ] + '.' } ]

  for rtext in rtext_list:
    parts = rtext[ 'value' ].split( '.' )
    zone = '.'.join( reversed( parts[ :3 ] ) ) + '.in-addr.arpa'
    try:
      zone_rtxt_map[ zone ].append( { 'value': parts[3], 'target': rtext[ 'target' ] } )
    except KeyError:
      zone_rtxt_map[ zone ] = [ { 'value': parts[3], 'target': rtext[ 'target' ] } ]

  for zone in set( list( zone_ptr_map.keys() ) + list( zone_rtxt_map.keys() ) ):
    record_map = { 'NS': [] }
    record_map[ 'SOA' ] = REVERSE_SOA.copy()
    record_map[ 'SOA' ][ 'zone' ] = zone

    for ns in settings.BIND_NS_NETWORKED_LIST:
      record_map[ 'NS' ].append( { 'name': '@', 'server': Networked.objects.get( pk=ns ).fqdn } )

    record_map[ 'PTR' ] = zone_ptr_map.get( zone, [] )
    record_map[ 'RTXT' ] = zone_rtxt_map.get( zone, [] )

    result = ''
    for rec_type in ( 'SOA', 'NS', 'PTR', 'RTXT' ):
      result += _render( rec_type, record_map[ rec_type ] )  # TODO: Sort record map

    filename = '{0}.zone'.format( zone )

    zone_file_list.append( ( filename, zone ) )

    yield filename, result


def genMasterFile( zone_dir, zone_file_list ):
  # result = 'allow_transfer {{ {0} }};\n'.format( ALLOW_TRANSFER )
  result = ''
  for filename, zone in zone_file_list:
    result += """
zone "{0}." {{
  type master;
  file "{1}";
}};
""".format( zone, os.path.join( zone_dir, filename ) )

  return result
