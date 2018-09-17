from math import log
from itertools import groupby


def IpIsV4( value ):  # ipv4 is signaled by 0000:0000:0000:0000:0000:FFFF:XXXX:XXXX
  if not isinstance( value, int ):
    raise ValueError( 'Invalid Ip Address' )

  return ( value & 0xffffffffffffffffffffffff00000000 ) == 0x00000000000000000000ffff00000000


def CIDRNetwork( prefix, ipv6 ):
  if not isinstance( prefix, int ) or prefix < 0 or ( ipv6 and prefix > 128 ) or ( not ipv6 and prefix > 32 ):
    raise ValueError( 'Invalid Prefix' )

  if ipv6:
    return ( 2 ** ( 128 - prefix ) ) - 1
  else:
    return ( 2 ** ( 32 - prefix ) ) - 1 + 0x0000000000000000000000000000ffff00000000


def CIDRNetmask( prefix, ipv6 ):
  if ipv6:
    return 0xffffffffffffffffffffffffffffffff - CIDRNetwork( prefix, True )
  else:
    return 0xffffffffffff - ( CIDRNetwork( prefix, False ) - 0x0000000000000000000000000000ffff00000000 )


def CIDRNetmaskToPrefix( value ):
  if not isinstance( value, int ):
    raise ValueError( 'Invalid Netmask' )

  if not IpIsV4( value ):
    tmp = 0xffffffffffffffffffffffffffffffff - value + 1
    return 128 - int( log( tmp, 2 ) )
  else:
    tmp = 0xffffffffffff - value + 1
    return 32 - int( log( tmp, 2 ) )


def CIDRNetworkSize( ip, prefix, include_unusable=False ):
  if not isinstance( ip, int ):
    raise ValueError( 'Invalid Ip Address' )

  if ip < 0 or ip > 0xffffffffffffffffffffffffffffffff:
    raise ValueError( 'Invalid Ip Address' )

  ipv6 = not IpIsV4( ip )
  if not isinstance( prefix, int ) or prefix < 0 or ( ipv6 and prefix > 128 ) or ( not ipv6 and prefix > 32 ):
    raise ValueError( 'Invalid Prefix' )

  if not ipv6:
    if prefix == 32:
      return 1

    elif prefix == 31:
      return 2

    elif include_unusable:
      return ( 2 ** ( 32 - prefix ) )

    else:
      return ( 2 ** ( 32 - prefix ) ) - 2

  else:
    if prefix == 128:
      return 1

    elif prefix == 127:
      return 2

    elif include_unusable:
      return ( 2 ** ( 128 - prefix ) )

    else:
      return ( 2 ** ( 128 - prefix ) ) - 2


def CIDRSubnet( ip, prefix, ipv6=None ):
  if ipv6 is None:
    ipv6 = not IpIsV4( ip )

  return CIDRNetmask( prefix, ipv6 ) & ip


def CIDRNetworkBounds( ip, prefix, include_unusable=False, as_offsets=False ):
  if not isinstance( ip, int ):
    raise ValueError( 'Invalid Ip Address' )

  if ip < 0 or ip > 0xffffffffffffffffffffffffffffffff:
    raise ValueError( 'Invalid Ip Address' )

  ipv6 = not IpIsV4( ip )
  if not isinstance( prefix, int ) or prefix < 0 or ( ipv6 and prefix > 128 ) or ( not ipv6 and prefix > 32 ):
    raise ValueError( 'Invalid Prefix' )

  net = CIDRNetwork( prefix, ipv6 )
  if as_offsets:
    if not ipv6:
      net -= 0x0000000000000000000000000000ffff00000000  # take this out, otherwise it get's added in twice
      if prefix == 32:
        return( 0, 0 )

      elif prefix == 31:
        return ( 0, 1 )

      elif include_unusable:
        return ( 0, net )

      else:
        return ( 1, net - 1 )

    else:
      if prefix == 128:
        return( 0, 0 )

      elif prefix == 127:
        return ( 0, 1 )

      elif include_unusable:
        return ( 0, net )

      else:  # I don't think ipv6 requires us to reserve the broadcast anymore, but who knows what kind of broken implementations there are out there, so just to be safe, for now
        return ( 1, net - 1 )

  base_ip = CIDRSubnet( ip, prefix, ipv6 )
  if not ipv6:
    net -= 0x0000000000000000000000000000ffff00000000  # take this out, otherwise it get's added in twice
    if prefix == 32:
      return( ip, ip )

    elif prefix == 31:
      return ( base_ip, base_ip + 1 )

    elif include_unusable:
      return ( base_ip, base_ip + net )

    else:
      return ( base_ip + 1, base_ip + net - 1)

  else:
    if prefix == 128:
      return( ip, ip )

    elif prefix == 127:
      return ( base_ip, base_ip + 1 )

    elif include_unusable:
      return ( base_ip, base_ip + net )

    else:  # I don't think ipv6 requires us to reserve the broadcast anymore, but who knows what kind of broken implementations there are out there, so just to be safe, for now
      return ( base_ip + 1, base_ip + net - 1)


def CIDRNetworkRange( value, prefix, include_unusable=False, as_offsets=False ):
  ( start, end ) = CIDRNetworkBounds( value, prefix, include_unusable, as_offsets )

  for i in range( start, ( end + 1 ) ):
    yield i


def StrToIp( value ):
  if value is None:
    return None

  if not isinstance( value, str ):
    raise ValueError( 'Invalid Ip Address' )

  result = 0

  if value.find( '.' ) != -1:
    if value.startswith( ':ffff:' ):
      value = value[ 6: ]
    part_list = value.split( '.' )
    if len( part_list ) != 4:
      raise ValueError( 'Invalid IPv4 Address' )

    while( part_list ):
      result <<= 8
      try:
        part = int( part_list.pop( 0 ) )
      except ValueError:
        raise ValueError( 'Invalid IPv4 Address' )

      if part > 255 or part < 0:
        raise ValueError( 'Invalid IPv4 Address' )

      result += part

    result += 0x0000000000000000000000000000ffff00000000

  elif value.find( ':' ) != -1:
    part_list = value.split( ':' )
    if len( part_list ) < 3 or len( part_list ) > 8:
      raise ValueError( 'Invalid IPv6 Address' )

    for i in range( 0, len( part_list ) ):
      if part_list[i] == '':
        if part_list[i + 1] == '':
          part_list = part_list[ 0:i ] + ( [ '0' ] * ( 10 - len( part_list  ) ) ) + part_list[ i + 2: ]
        else:
          part_list = part_list[ 0:i ] + ( [ '0' ] * ( 9 - len( part_list ) ) ) + part_list[ i + 1: ]
        break

    if part_list[-1] == '':
      part_list[-1] = '0'

    for i in range( 0, 8 ):
      result <<= 16
      try:
        result += int( part_list[i], base=16 )
      except ValueError:
        raise ValueError( 'Invalid IPv6 Address' )

  else:
    raise ValueError( 'Invalid Ip Address' )

  return result


def IpToStr( value, as_v6=False ):
  if value is None:
    return None

  if not isinstance( value, int ):
    raise ValueError( 'Invalid Ip Address' )

  if value < 0 or value > 0xffffffffffffffffffffffffffffffff:
    raise ValueError( 'Invalid Ip Address' )

  part_list = []
  if IpIsV4( value ):
    for i in range( 0, 4 ):
      part_list.insert( 0, '{0}'.format( value & 0xff ) )
      value >>= 8

    if as_v6:
      return ':ffff:{0}'.format( '.'.join( part_list ) )
    else:
      return '.'.join( part_list )

  else:
    for i in range( 0, 8 ):
      part_list.insert( 0, '{0:x}'.format( value & 0xffff ) )  # as hex
      value >>= 16

    item_list = []
    count_list = []
    for item, grouper in groupby( part_list ):
      count = len( list( grouper ) )
      if item != '0':
        item_list += [ item ] * count
        count_list += [ 0 ] * count
      else:
        item_list.append( item )
        count_list.append( count )

    max_count = max( count_list )
    if max_count == 1:
      return ':'.join( item_list )

    part_list = []
    max_index = count_list.index( max_count )
    for i in range( 0, len( count_list ) ):
      if item_list[i] != '0':
        part_list.append( item_list[i] )
        continue

      if i == max_index:
        part_list.append( '' )
      else:
        part_list += [ '0' ] * count_list[i]

    if part_list[0] == '':
      part_list.insert( 0, '' )
    elif part_list[-1] == '':
      part_list.append( '' )

    if len( part_list ) == 2:
      return '::{0}'.format( part_list[1] )

    return ':'.join( part_list )
