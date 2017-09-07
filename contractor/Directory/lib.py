

MASTER_NS = 'contractor.myzone.local.'
MASTER_NS_IP = '10.0.0.1'
NS_SERVERS = [ 'ns1.myzone.local.', 'ns2.myzone.local.' ]
ALLOW_TRANSFER = [ '127.0.0.1' ]

TEMPLATES = {}

TEMPLATES[ 'SOA' ] = """$TTL {ttl}
$ORIGIN {zone}
@  IN SOA {master} {email} (
            **ZONE_SERIAL**
            {refresh}
            {retry}
            {expire}
            {minimum}
          )
"""
TEMPLATES[ 'NS' ] = '{0>:50} IN NS {server}'.format( '' )
TEMPLATES[ 'MX' ] = '{name:>50} IN MX {priority:>4} {target}'
TEMPLATES[ 'A' ] = '{name:>50} IN A {address}'
TEMPLATES[ 'AAAA' ] = '{name:>50} IN AAAA {address}'
TEMPLATES[ 'PTR' ] = '{value:>50} IN PTR {target}'
TEMPLATES[ 'CNAME' ] = '{name:>50} IN CNAME {target}'
TEMPLATES[ 'TXT' ] = '{name:>50} IN TXT {target}'
TEMPLATES[ 'SRV' ] = '{name:>50} IN SRV {priority:>4} {weight:>4} {name:<50} {port:<5} {target}'
TEMPLATES[ 'SIG' ] = '{name:>50} IN SIG {sig}'


def _render( type, parms ):
  if isinstance( parms, list ):
    return ''.join( [ _render( type, i ) for i in parms ] )

  try:
    return TEMPLATES[ type ].format( parms ) + '\n'
  except KeyError:
    raise ValueError( 'Invalid Record Type "{0}"'.format( type ) )


def _getNetworkedEntries( networked ):
  result = {}

  result[ 'A' ] = []
  result[ 'CNAME' ] = []
  result[ 'TXT' ] = []
  result[ 'PTR' ] = []

  return result


def genZone( zone, ptr_list, zone_file_list ):
  record_map = dict( zip( TEMPLATES.keys(), [] * len( TEMPLATES.keys() ) ) )

  for site in zone.site_set.all():
    for networked in site.networked_set.all():
      entry_list = _getNetworkedEntries( networked )
      for type in entry_list:
        record_map[ type ] += entry_list[ type ]

  for entry in zone.entry_set.all():
    record_map[ entry.type ].append( {
                                       'name': entry.name,
                                       'priority': entry.priority,
                                       'weight': entry.weight,
                                       'port': entry.port,
                                       'target': entry.target
                                     } )

  record_map[ 'SOA' ] = [ {
                            'zone': zone.fqdn,
                            'master': MASTER_NS,
                            'ttl': zone.ttl,
                            'email': zone.email.replace( '@', '.' ),
                            'refresh': zone.refresh,
                            'retry': zone.retry,
                            'expire': zone.expire,
                            'minimum': zone.minimum
                          } ]

  record_map[ 'NS' ] = [ { 'server': i } for i in NS_SERVERS ]

  ptr_list.append( record_map[ 'PTR' ] )
  del record_map[ 'PTR' ]

  result = ''
  for type in ( 'SOA', 'NS', 'SIG', 'SRV', 'A', 'AAAA', 'CNAME', 'TXT', 'PTR' ):
    result += _render( type, sorted( record_map[ type ] ) )

  zone_file_list.append( ( zone.name, zone.name ) )

  return zone.name, result


def genPtrZones( ptr_list, zone_file_list ):
  for ptr in ptr_list:
    filename = '{0}.'.format( ptr )
    zone_file_list.append( ( filename, filename ) )
    yield filename, 'stuff'


def genMasterFile( zone_dir, zone_file_list ):
  result = 'allow_transfer {{ {0} }}'.format( ALLOW_TRANSFER )
  for filename, zone in zone_file_list:
    result += """
{0}
{
  file {1}
  master {2}
}
""".format( zone, os.path.join( zone_dir, filename ), MASTER_NS_IP )
  return result
