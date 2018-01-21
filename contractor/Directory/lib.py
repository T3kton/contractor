import os

MASTER_NS = 'contractor.myzone.local'
MASTER_NS_IP = '10.0.0.1'
ALLOW_TRANSFER = [ '127.0.0.1' ]

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
TEMPLATES[ 'NS' ] = '{name:<50} IN NS   {server}'
TEMPLATES[ 'MX' ] = '{name:<50} IN MX   {priority:>4} {target}'
TEMPLATES[ 'A' ] = '{name:<50} IN A    {address}'
TEMPLATES[ 'AAAA' ] = '{name:<50} IN AAAA {address}'
TEMPLATES[ 'PTR' ] = '{value:<50} IN PTR  {target}'
TEMPLATES[ 'CNAME' ] = '{name:<50} IN CNAME {target}'
TEMPLATES[ 'TXT' ] = '{name:<50} IN TXT  {target}'
TEMPLATES[ 'SRV' ] = '{name:<50} IN SRV  {priority:>4} {weight:>4} {name:<50} {port:>5} {target}'
TEMPLATES[ 'SIG' ] = '{name:<50} IN SIG  {sig}'

REVERSE_SOA = { 'ttl': 3600, 'refresh': 86400, 'retry': 7200, 'expire': 36000, 'minimum': 172800, 'master': MASTER_NS, 'email': 'hostmaster.site1.local' }
REVERSE_NS = [ 'contractor.site1.local.' ]


def _render( rec_type, parms ):
  if isinstance( parms, list ):
    return ''.join( [ _render( rec_type, i ) for i in parms ] )

  try:
    template = TEMPLATES[ rec_type ]
  except KeyError:
    raise ValueError( 'Invalid Record Type "{0}"'.format( rec_type ) )

  return template.format( **parms ) + '\n'


def _getNetworkedEntries( networked ):
  networked = networked.subclass
  result = {}

  result[ 'A' ] = [ { 'name': networked.hostname, 'address': networked.primary_ip } ]
  result[ 'CNAME' ] = []
  result[ 'TXT' ] = []
  result[ 'PTR' ] = [ { 'target': networked.fqdn, 'value': networked.primary_ip } ]

  return result


def genZone( zone, ptr_list, zone_file_list ):
  record_map = {}
  for rec_type in TEMPLATES.keys():
    record_map[ rec_type ] = []

  zone_fqdn = zone.fqdn

  for ns in zone.ns_list:
    record_map[ 'NS' ].append( { 'name': '@', 'server': ns } )
    ( hostname, domain ) = ns.split( '.', 1 )
    if domain != zone_fqdn:
      record_map[ 'A' ].append( { 'name': ns, 'address': '192.168.200.53' }  )

  for subZone in zone.zone_set.all():
    for ns in subZone.ns_list:
      record_map[ 'NS' ].append( { 'name': subZone.name, 'server': ns } )
      ( hostname, domain ) = ns.split( '.', 1 )
      if domain != zone_fqdn:
        record_map[ 'A' ].append( { 'name': ns, 'address': '192.168.200.53' }  )

  for site in zone.site_set.all():
    for networked in site.networked_set.all():
      entry_list = _getNetworkedEntries( networked )
      for entry_type in entry_list:
        record_map[ entry_type ] += entry_list[ entry_type ]

  for entry in zone.entry_set.all():
    record_map[ entry.type ].append( {
                                       'name': entry.name,
                                       'priority': entry.priority,
                                       'weight': entry.weight,
                                       'port': entry.port,
                                       'target': entry.target
                                     } )

  record_map[ 'SOA' ] = [ {
                            'zone': zone_fqdn,
                            'master': MASTER_NS,
                            'ttl': zone.ttl,
                            'email': zone.email.replace( '@', '.' ),
                            'refresh': zone.refresh,
                            'retry': zone.retry,
                            'expire': zone.expire,
                            'minimum': zone.minimum
                          } ]

  ptr_list += record_map[ 'PTR' ]

  del record_map[ 'PTR' ]

  result = ''
  for rec_type in ( 'SOA', 'NS', 'SIG', 'SRV', 'A', 'AAAA', 'CNAME', 'TXT' ):
    result += _render( rec_type, record_map[ rec_type ] )  # TODO: Sort record map

  zone_file_list.append( ( zone.name, zone_fqdn ) )

  return zone.name, result


def genPtrZones( ptr_list, zone_file_list ):
  zone_list = {}

  for ptr in ptr_list:
    parts = ptr[ 'value' ].split( '.' )
    zone = '.'.join( reversed( parts[ :3 ] ) ) + '.in-addr.arpa'
    try:
      zone_list[ zone ].append( { 'value': parts[3], 'target': ptr[ 'target' ] + '.' } )
    except KeyError:
      zone_list[ zone ] = [ { 'value': parts[3], 'target': ptr[ 'target' ] + '.' } ]

  for zone in zone_list:
    record_map = { 'NS': [], 'PTR': [], 'TXT': [] }
    record_map[ 'SOA' ] = REVERSE_SOA.copy()
    record_map[ 'SOA' ][ 'zone' ] = zone

    for ns in REVERSE_NS:
      record_map[ 'NS' ].append( { 'name': '@', 'server': ns } )

    record_map[ 'PTR' ] = zone_list[ zone ]

    result = ''
    for rec_type in ( 'SOA', 'NS', 'PTR', 'TXT' ):
      result += _render( rec_type, record_map[ rec_type ] )  # TODO: Sort record map

    zone_file_list.append( ( zone, zone ) )

    yield zone, result


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
