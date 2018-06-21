import os

from django.conf import settings

from contractor.Directory.models import Zone

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
TEMPLATES[ 'TXT' ] = '{name:<50} IN TXT   {target}'
TEMPLATES[ 'SRV' ] = '{name:<50} IN SRV   {priority:>4} {weight:>4} {name:<50} {port:>5} {target}'
TEMPLATES[ 'SIG' ] = '{name:<50} IN SIG   {sig}'

REVERSE_SOA = { 'ttl': 3600, 'refresh': 86400, 'retry': 7200, 'expire': 36000, 'minimum': 172800, 'master': settings.BIND_NS_LIST[0], 'email': settings.BIND_SOA_EMAIL }


def getHostIp( fqdn ):
  parts = fqdn.split( '.' )
  if parts[-1] == '':
    parts.pop()

  # We are going to start at the end, work backward till the zone names stop matching, then try for hostname and possibly interface
  zone = None
  try:
    name = parts.pop()
    zone = Zone.objects.get( name=name )
    while parts:
      name = parts.pop()
      zone = zone.zone_set.get( name=name )
  except Zone.DoesNotExist:
    pass

  if zone is None:
    raise ValueError( 'Unable to find top level zone "{0}"'.format( name ) )

  hostname = name

  networked = None
  for site in zone.site_set.all():
    for networked in site.networked_set.all():
      if networked.hostname == hostname:
        break

  if networked is None:
    raise ValueError( 'Unable to find hostname "{0}" in zone "{1}"'.format( hostname, zone ) )

  if len( parts ) == 1:
    return networked.address_set.get( interface_name=parts[0] ).ip_address

  elif len( parts ) == 0:
    return networked.primary_ip

  raise ValueError( 'Not sure what to do with "{0}" for host "{1}" in "{2}"'.format( parts, networked, zone) )


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

  if networked.primary_ip is None:
    return result

  ip_addr = networked.primary_ip
  iface = networked.primary_interface

  result[ 'A' ] = [ { 'name': '{0}.{1}'.format( iface.name, networked.hostname ), 'address': ip_addr } ]
  result[ 'CNAME' ] = [ { 'name': networked.hostname, 'target': '{0}.{1}'.format( iface.name, networked.hostname ) } ]
  result[ 'TXT' ] = []
  result[ 'PTR' ] = [ { 'target': networked.fqdn, 'value': ip_addr } ]

  return result


def genZone( zone, ptr_list, zone_file_list ):
  record_map = {}
  for rec_type in TEMPLATES.keys():
    record_map[ rec_type ] = []

  zone_fqdn = zone.fqdn

  for ns in settings.BIND_NS_LIST:
    record_map[ 'NS' ].append( { 'name': '@', 'server': ns } )
    if ns.endswith( zone_fqdn ):
      ns_ip = getHostIp( ns )
      record_map[ 'A' ].append( { 'name': ns[ :-len( zone_fqdn ) - 1], 'address': ns_ip } )

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
                            'master': settings.BIND_NS_LIST[ 0 ],
                            'ttl': zone.ttl,
                            'email': settings.BIND_SOA_EMAIL,
                            'refresh': zone.refresh,
                            'retry': zone.retry,
                            'expire': zone.expire,
                            'minimum': zone.minimum
                          } ]

  ptr_list += record_map[ 'PTR' ]

  del record_map[ 'PTR' ]

  result = ''
  for rec_type in ( 'SOA', 'NS', 'SIG', 'SRV', 'A', 'AAAA', 'CNAME', 'TXT' ):
    result += _render( rec_type, record_map[ rec_type ] )  # TODO: Sort record map, and get rid of duplicates

  filename = '{0}.zone'.format( zone_fqdn )

  zone_file_list.append( ( filename, zone_fqdn ) )

  return filename, result


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

    for ns in settings.BIND_NS_LIST:
      record_map[ 'NS' ].append( { 'name': '@', 'server': ns } )

    record_map[ 'PTR' ] = zone_list[ zone ]

    result = ''
    for rec_type in ( 'SOA', 'NS', 'PTR', 'TXT' ):
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
