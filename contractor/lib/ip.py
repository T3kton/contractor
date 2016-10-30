from math import log

def IpIsV4( value ): # ipv4 is signaled by 0000:0000:0000:0000:0000:FFFF:XXXX:XXXX
  return ( value & 0xffffffffffffffffffffffff00000000 ) == 0x00000000000000000000ffff00000000

def CIDRNetwork( prefix, ipv6 ):
  if ipv6:
    return ( 2 ** ( 128 - prefix ) ) - 1
  else:
    return ( 2 ** ( 32 - prefix ) ) - 1

def CIDRNetmask( prefix, ipv6=False ):
  if ipv6:
    return 0xffffffffffffffffffffffffffffffff - CIDRNetwork( prefix, True )
  else:
    return 0xffffffff - CIDRNetwork( prefix, False )

def CIDRNetmaskToPrefix( value, ipv6=False ):
  if ipv6:
    tmp = 0xffffffffffffffffffffffffffffffff - value + 1
    return 128 - int( log( tmp, 2 ) )
  else:
    tmp = 0xffffffff - value + 1
    return 32 - int( log( tmp, 2 ) )

def CIDRNetworkBounds( value, include_unusable=False ):
  try:
    ( ip, prefix ) = value.split( '/' )
    prefix = int( prefix )
  except ValueError:
    raise ValueError( 'Invalid CIDR range "{0}"'.format( value ) )

  ip = StrToIp( ip )
  if IpIsV4( ip ):
    net = CIDRNetwork( prefix, False )
    netmask = CIDRNetmask( prefix, False )
    base_ip = net & netmask
    if prefix == 32:
      return( ip, ip )

    elif prefix == 31:
      return ( base_ip, base_ip + 1 )

    elif include_unusable:
      return ( base_ip, base_ip + net )

    else:
      return ( base_ip + 1, base_ip + net - 1)

  else:
    net = CIDRNetwork( prefix, True )
    netmask = CIDRNetmask( prefix, True )
    base_ip = net & netmask

    if prefix == 128:
      return( ip, ip )

    elif prefix == 127:
      return ( base_ip, base_ip + 1 )

    elif include_unusable:
      return ( base_ip, base_ip + net )

    else: # I don't think ipv6 requires us to reserve the broadcast anymore, but who knows what kind of broken implementations there are out there, so just to be safe, for now
      return ( base_ip + 1, base_ip + net - 1)


def CIDRNetworkRange( value, include_unusable=False ): # make /24 /23 compatible for ipv4
  ( start, end ) = CIDRNetworkBounds( value, include_unusable )

  result = []
  for i in range( start, ( end + 1 ) ):
    result.append( IpToStr( i ) )

  return result


def StrToIp( value ):
  result = 0

  if value.find( '.' ) != -1:
    parts = value.split( '.' )
    if len( parts ) != 4:
      raise ValueError( 'Invalid IPv4 Address, "{0}"'.format( value ) )

    while( parts ):
      result <<= 8
      try:
        result += int( parts.pop( 0 ) )
      except ValueError:
        raise ValueError( 'Invalid IPv4 Address, "{0}"'.format( value ) )

    result += 0x0000000000000000000000000000ffff00000000

  elif value.find( ':' ) != -1:
    parts = value.split( ':' )
    if len( parts ) < 3 or len( parts ) > 8:
      raise ValueError( 'Invalid IPv6 Address, "{0}}"'.format( value ) )
    print( parts )
    for i in range( 0, len( parts ) ):
      if parts[i] == '':
        if parts[i + 1] == '':
          parts = parts[ 0:i ] + ( [ '0' ] * ( 10 - len( parts  ) ) ) + parts[ i + 2: ]
        else:
          parts = parts[ 0:i ] + ( [ '0' ] * ( 9 - len( parts ) ) ) + parts[ i + 1: ]
        break

    print( parts )
    for i in range( 0, 8 ):
      result <<= 16
      try:
        result += int( parts[i], base=16 )
      except ValueError:
        raise ValueError( 'Invalid IPv6 Address, "{0}"'.format( value ) )

  else:
    raise ValueError( 'Invalid IP Address, "{0}"'.format( value ) )

  return result


def IpToStr( value, force_v6=False ):
  if not isinstance( value, int ):
    raise ValueError( 'ip must be numeric' )

  if value < 0 or value > 0xffffffffffffffffffffffffffffffff:
    raise ValueError( 'ip value is invalid' )

  parts = []
  if IpIsV4( value ) and not force_v6:
    for i in range( 0, 4 ):
      parts.insert( 0, '{0}'.format( value & 0xff ) )
      value >>= 8

    return '.'.join( parts )
  else:
    for i in range( 0, 8 ):
      parts.insert( 0, '{0:x}'.format( value & 0xffff ) ) # as hex
      value >>= 16

    # find the longest group of 0s and compress them to ::

    return ':'.join( parts )
