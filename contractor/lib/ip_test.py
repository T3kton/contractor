import pytest

from contractor.lib.ip import IpIsV4, StrToIp, IpToStr, CIDRNetwork, CIDRNetmask, CIDRNetmaskToPrefix, CIDRNetworkSize, CIDRNetworkBounds, CIDRNetworkRange


def test_isv4():
  assert IpIsV4( 281470681743360 )
  assert IpIsV4( 281470681743361 )
  assert not IpIsV4( 1 )
  assert not IpIsV4( 0 )
  assert not IpIsV4( 281470681743359 )


def test_strtoip():
  with pytest.raises( ValueError ):
    StrToIp( '127' )
  with pytest.raises( ValueError ):
    StrToIp( '127.00.1' )
  with pytest.raises( ValueError ):
    StrToIp( '127.0.1' )
  with pytest.raises( ValueError ):
    StrToIp( 'a.0.0.0' )
  with pytest.raises( ValueError ):
    StrToIp( '0.a.0.0' )
  with pytest.raises( ValueError ):
    StrToIp( '0.0.a.0' )
  with pytest.raises( ValueError ):
    StrToIp( '0.0.0.a' )
  with pytest.raises( ValueError ):
    StrToIp( '256.0.0.0' )
  with pytest.raises( ValueError ):
    StrToIp( '0.256.0.0' )
  with pytest.raises( ValueError ):
    StrToIp( '0.0.256.0' )
  with pytest.raises( ValueError ):
    StrToIp( '0.0.0.256' )
  with pytest.raises( ValueError ):
    StrToIp( '0.0.0.-1' )
  with pytest.raises( ValueError ):
    StrToIp( '0.0.-1.0' )
  with pytest.raises( ValueError ):
    StrToIp( '0.-1.0.0' )
  with pytest.raises( ValueError ):
    StrToIp( '-1.0.0.0' )
  assert StrToIp( '0.0.0.0' ) == 281470681743360
  assert StrToIp( '127.0.0.1' ) == 281472812449793
  assert StrToIp( '1.2.3.4' ) == 281470698652420
  assert StrToIp( ':ffff:0.0.0.0' ) == 281470681743360
  assert StrToIp( ':ffff:127.0.0.1' ) == 281472812449793
  assert StrToIp( ':ffff:1.2.3.4' ) == 281470698652420
  with pytest.raises( ValueError ):
    StrToIp( ':fff:0.0.0.0' )

  with pytest.raises( ValueError ):
    StrToIp( ':' )
  with pytest.raises( ValueError ):
    StrToIp( ':::' )
  with pytest.raises( ValueError ):
    StrToIp( '::x' )
  assert StrToIp( '::' ) == 0
  assert StrToIp( '::1' ) == 1
  assert StrToIp( '::a' ) == 10
  assert StrToIp( '::ffff' ) == 65535
  assert StrToIp( '2001:db8:0:0:1:0:0:1' ) == 42540766411282592856904266426630537217
  assert StrToIp( '2001:0db8:0:0:1:0:0:1' ) == 42540766411282592856904266426630537217
  assert StrToIp( '2001:db8::1:0:0:1' ) == 42540766411282592856904266426630537217
  assert StrToIp( '2001:db8::0:1:0:0:1' ) == 42540766411282592856904266426630537217
  assert StrToIp( '2001:0db8::1:0:0:1' ) == 42540766411282592856904266426630537217
  assert StrToIp( '2001:db8:0:0:1::1' ) == 42540766411282592856904266426630537217
  assert StrToIp( '2001:db8:0000:0:1::1' ) == 42540766411282592856904266426630537217
  assert StrToIp( '2001:DB8:0:0:1::1' ) == 42540766411282592856904266426630537217
  with pytest.raises( ValueError ):
    StrToIp( '2001:db8::1::1' )
  assert StrToIp( '2001:db8:0:0:0:0:0:1' ) == 42540766411282592856903984951653826561
  assert StrToIp( '2001:db8:0:0:0::1' ) == 42540766411282592856903984951653826561
  assert StrToIp( '2001:db8:0:0::1' ) == 42540766411282592856903984951653826561
  assert StrToIp( '2001:db8:0::1' ) == 42540766411282592856903984951653826561
  assert StrToIp( '2001:db8::1' ) == 42540766411282592856903984951653826561
  with pytest.raises( ValueError ):
    StrToIp( '::db8::1' )
  with pytest.raises( ValueError ):
    StrToIp( '2001:db8::0::1' )
  assert StrToIp( '2001:0:0:0:1:0:0:1' ) == 42540488161975842760550637900276957185
  assert StrToIp( '2001::1:0:0:1' ) == 42540488161975842760550637900276957185
  assert StrToIp( '2001:0:0:0:1::1' ) == 42540488161975842760550637900276957185
  assert StrToIp( '2001:0:1:0:1:0:1:0' ) == 42540488161977051686370252529451728896
  assert StrToIp( '2001::' ) == 42540488161975842760550356425300246528

  assert StrToIp( None ) is None


def test_iptostr():
  assert IpToStr( 0 ) == '::'
  assert IpToStr( 1 ) == '::1'
  assert IpToStr( 10 ) == '::a'
  assert IpToStr( 65535 ) == '::ffff'
  assert IpToStr( 0, False ) == '::'
  assert IpToStr( 1, False ) == '::1'
  assert IpToStr( 10, False ) == '::a'
  assert IpToStr( 65535, False ) == '::ffff'
  assert IpToStr( 0, True ) == '::'
  assert IpToStr( 1, True ) == '::1'
  assert IpToStr( 10, True ) == '::a'
  assert IpToStr( 65535, True ) == '::ffff'
  assert IpToStr( 42540766411282592856903984951653826561 ) == '2001:db8::1'
  assert IpToStr( 42540766411282592856904266426630537217 ) == '2001:db8::1:0:0:1'
  assert IpToStr( 42540488161975842760550637900276957185 ) == '2001::1:0:0:1'
  assert IpToStr( 42540488161977051686370252529451728896 ) == '2001:0:1:0:1:0:1:0'
  assert IpToStr( 42540488161975842760550356425300246528 ) == '2001::'
  assert IpToStr( 42540766411282592856903984951653826561, False ) == '2001:db8::1'
  assert IpToStr( 42540766411282592856904266426630537217, False ) == '2001:db8::1:0:0:1'
  assert IpToStr( 42540488161975842760550637900276957185, False ) == '2001::1:0:0:1'
  assert IpToStr( 42540488161977051686370252529451728896, False ) == '2001:0:1:0:1:0:1:0'
  assert IpToStr( 42540488161975842760550356425300246528, False ) == '2001::'
  assert IpToStr( 42540766411282592856903984951653826561, True ) == '2001:db8::1'
  assert IpToStr( 42540766411282592856904266426630537217, True ) == '2001:db8::1:0:0:1'
  assert IpToStr( 42540488161975842760550637900276957185, True ) == '2001::1:0:0:1'
  assert IpToStr( 42540488161977051686370252529451728896, True ) == '2001:0:1:0:1:0:1:0'
  assert IpToStr( 42540488161975842760550356425300246528, True ) == '2001::'
  assert IpToStr( 281470681743360 ) == '0.0.0.0'
  assert IpToStr( 281470681743361 ) == '0.0.0.1'
  assert IpToStr( 281472812449793 ) == '127.0.0.1'
  assert IpToStr( 281470698652420 ) == '1.2.3.4'
  assert IpToStr( 281470681743360, False ) == '0.0.0.0'
  assert IpToStr( 281470681743361, False ) == '0.0.0.1'
  assert IpToStr( 281472812449793, False ) == '127.0.0.1'
  assert IpToStr( 281470698652420, False ) == '1.2.3.4'
  assert IpToStr( 281470681743360, True ) == ':ffff:0.0.0.0'
  assert IpToStr( 281470681743361, True ) == ':ffff:0.0.0.1'
  assert IpToStr( 281472812449793, True ) == ':ffff:127.0.0.1'
  assert IpToStr( 281470698652420, True ) == ':ffff:1.2.3.4'
  assert IpToStr( StrToIp( '1:1:1:1:2:3:4:5' ) ) == '1:1:1:1:2:3:4:5'
  assert IpToStr( StrToIp( '2:2:2:2:2:3:4:5' ) ) == '2:2:2:2:2:3:4:5'
  assert IpToStr( StrToIp( '0:0:0:0:2:3:4:5' ) ) == '::2:3:4:5'
  assert IpToStr( StrToIp( '1:2:2:2:2:3:4:5' ) ) == '1:2:2:2:2:3:4:5'
  assert IpToStr( StrToIp( '1:0:0:0:0:3:4:5' ) ) == '1::3:4:5'
  assert IpToStr( StrToIp( '1:1:1:1:0:0:4:5' ) ) == '1:1:1:1::4:5'
  assert IpToStr( StrToIp( '1:1:1:1:0:0:0:0' ) ) == '1:1:1:1::'

  with pytest.raises( ValueError ):
    IpToStr( -1 )
  with pytest.raises( ValueError ):
    IpToStr( 0x100000000000000000000000000000000 )
  with pytest.raises( ValueError ):
    IpToStr( '0' )

  assert IpToStr( None ) is None


def test_cidrnetwork():
  assert CIDRNetwork( 24, False ) == StrToIp( '0.0.0.255' )
  assert CIDRNetwork( 25, False ) == StrToIp( '0.0.0.127' )
  assert CIDRNetwork( 26, False ) == StrToIp( '0.0.0.63' )
  assert CIDRNetwork( 27, False ) == StrToIp( '0.0.0.31' )
  assert CIDRNetwork( 23, False ) == StrToIp( '0.0.1.255' )
  assert CIDRNetwork( 32, False ) == StrToIp( '0.0.0.0' )
  assert CIDRNetwork( 31, False ) == StrToIp( '0.0.0.1' )
  assert CIDRNetwork( 8, False ) == StrToIp( '0.255.255.255' )
  assert CIDRNetwork( 8, True ) == StrToIp( '00ff:ffff:ffff:ffff:ffff:ffff:ffff:ffff' )
  assert CIDRNetwork( 16, True ) == StrToIp( '0:ffff:ffff:ffff:ffff:ffff:ffff:ffff' )
  assert CIDRNetwork( 128, True ) == StrToIp( '::' )
  assert CIDRNetwork( 127, True ) == StrToIp( '::1' )
  assert CIDRNetwork( 120, True ) == StrToIp( '::ff' )
  assert CIDRNetwork( 32, True ) == StrToIp( '::ffff:ffff:ffff:ffff:ffff:ffff' )
  assert CIDRNetwork( 64, True ) == StrToIp( '::ffff:ffff:ffff:ffff' )
  assert CIDRNetwork( 96, True ) == StrToIp( '::ffff:ffff' )
  assert CIDRNetwork( 80, True ) == StrToIp( '::ffff:ffff:ffff' )

  with pytest.raises( ValueError ):
    CIDRNetwork( -1, True )
  with pytest.raises( ValueError ):
    CIDRNetwork( -1, False )
  with pytest.raises( ValueError ):
    CIDRNetwork( 33, False )
  with pytest.raises( ValueError ):
    CIDRNetwork( 129, True )
  with pytest.raises( ValueError ):
    CIDRNetwork( 'a', False )
  with pytest.raises( ValueError ):
    CIDRNetwork( 'a', True )


def test_cidrnetmask():
  assert CIDRNetmask( 24, False ) == StrToIp( '255.255.255.0' )
  assert CIDRNetmask( 25, False ) == StrToIp( '255.255.255.128' )
  assert CIDRNetmask( 26, False ) == StrToIp( '255.255.255.192' )
  assert CIDRNetmask( 27, False ) == StrToIp( '255.255.255.224' )
  assert CIDRNetmask( 23, False ) == StrToIp( '255.255.254.0' )
  assert CIDRNetmask( 32, False ) == StrToIp( '255.255.255.255' )
  assert CIDRNetmask( 31, False ) == StrToIp( '255.255.255.254' )
  assert CIDRNetmask( 8, False ) == StrToIp( '255.0.0.0' )
  assert CIDRNetmask( 8, True ) == StrToIp( 'ff00::' )
  assert CIDRNetmask( 16, True ) == StrToIp( 'ffff::' )
  assert CIDRNetmask( 128, True ) == StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff' )
  assert CIDRNetmask( 127, True ) == StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:fffe' )
  assert CIDRNetmask( 120, True ) == StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ff00' )
  assert CIDRNetmask( 32, True ) == StrToIp( 'ffff:ffff::' )
  assert CIDRNetmask( 64, True ) == StrToIp( 'ffff:ffff:ffff:ffff::' )
  assert CIDRNetmask( 96, True ) == StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff::' )
  assert CIDRNetmask( 80, True ) == StrToIp( 'ffff:ffff:ffff:ffff:ffff::' )

  with pytest.raises( ValueError ):
    CIDRNetmask( -1, True )
  with pytest.raises( ValueError ):
    CIDRNetmask( -1, False )
  with pytest.raises( ValueError ):
    CIDRNetmask( 33, False )
  with pytest.raises( ValueError ):
    CIDRNetmask( 129, True )
  with pytest.raises( ValueError ):
    CIDRNetmask( 'a', False )
  with pytest.raises( ValueError ):
    CIDRNetmask( 'a', True )


def test_cidrnetmasktoprefix():
  assert CIDRNetmaskToPrefix( StrToIp( '255.255.255.0' ) ) == 24
  assert CIDRNetmaskToPrefix( StrToIp( '255.255.255.128' ) ) == 25
  assert CIDRNetmaskToPrefix( StrToIp( '255.255.255.192' ) ) == 26
  assert CIDRNetmaskToPrefix( StrToIp( '255.255.255.224' ) ) == 27
  assert CIDRNetmaskToPrefix( StrToIp( '255.255.254.0' ) ) == 23
  assert CIDRNetmaskToPrefix( StrToIp( '255.255.255.255' ) ) == 32
  assert CIDRNetmaskToPrefix( StrToIp( '255.255.255.254' ) ) == 31
  assert CIDRNetmaskToPrefix( StrToIp( '255.0.0.0' ) ) == 8
  assert CIDRNetmaskToPrefix( StrToIp( 'ff00::' ) ) == 8
  assert CIDRNetmaskToPrefix( StrToIp( 'ffff::' ) ) == 16
  assert CIDRNetmaskToPrefix( StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff' ) ) == 128
  assert CIDRNetmaskToPrefix( StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:fffe' ) ) == 127
  assert CIDRNetmaskToPrefix( StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ff00' ) ) == 120

  assert CIDRNetmaskToPrefix( StrToIp( '10.0.0.3' ) ) == 1  # yea, with CIDR are relying on leading bits being set

  with pytest.raises( ValueError ):
    CIDRNetmaskToPrefix( '127.0.0.1' )


def test_cidrnetworksize():
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 32 ) == 1
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 32, True ) == 1
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 32, False ) == 1
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 31 ) == 2
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 31, True ) == 2
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 31, False ) == 2
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 30 ) == 2
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 30, True ) == 4
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 30, False ) == 2
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 29 ) == 6
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 29, True ) == 8
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 29, False ) == 6
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 8 ) == 16777214
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 8, True ) == 16777216
  assert CIDRNetworkSize( StrToIp( '3.2.5.3' ), 8, False ) == 16777214

  assert CIDRNetworkSize( StrToIp( '::3' ), 128 ) == 1
  assert CIDRNetworkSize( StrToIp( '::3' ), 128, True ) == 1
  assert CIDRNetworkSize( StrToIp( '::3' ), 128, False ) == 1
  assert CIDRNetworkSize( StrToIp( '::3' ), 127 ) == 2
  assert CIDRNetworkSize( StrToIp( '::3' ), 127, True ) == 2
  assert CIDRNetworkSize( StrToIp( '::3' ), 127, False ) == 2
  assert CIDRNetworkSize( StrToIp( '::3' ), 126 ) == 2
  assert CIDRNetworkSize( StrToIp( '::3' ), 126, True ) == 4
  assert CIDRNetworkSize( StrToIp( '::3' ), 126, False ) == 2
  assert CIDRNetworkSize( StrToIp( '::3' ), 125 ) == 6
  assert CIDRNetworkSize( StrToIp( '::3' ), 125, True ) == 8
  assert CIDRNetworkSize( StrToIp( '::3' ), 125, False ) == 6
  assert CIDRNetworkSize( StrToIp( '::3' ), 8 ) == 1329227995784915872903807060280344574
  assert CIDRNetworkSize( StrToIp( '::3' ), 8, True ) == 1329227995784915872903807060280344576
  assert CIDRNetworkSize( StrToIp( '::3' ), 8, False ) == 1329227995784915872903807060280344574

  with pytest.raises( ValueError ):
    CIDRNetworkSize( -1, 0 )
  with pytest.raises( ValueError ):
    CIDRNetworkSize( 0x100000000000000000000000000000000, 0 )
  with pytest.raises( ValueError ):
    CIDRNetworkSize( StrToIp( '255.255.255.255' ), 33 )
  with pytest.raises( ValueError ):
    CIDRNetworkSize( StrToIp( '0.0.0.0' ), 33 )
  with pytest.raises( ValueError ):
    CIDRNetworkSize( StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff' ), 129 )
  with pytest.raises( ValueError ):
    CIDRNetworkSize( StrToIp( '::' ), 129 )
  with pytest.raises( ValueError ):
    CIDRNetworkSize( '::', 129 )


def test_cidrnetworkbounds():
  assert CIDRNetworkBounds( StrToIp( '10.0.0.0' ), 8 ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.255.255.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.0' ), 8, False ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.255.255.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.0' ), 8, True ) == ( StrToIp( '10.0.0.0' ), StrToIp( '10.255.255.255' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.1' ), 8 ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.255.255.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.1' ), 8, False ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.255.255.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.1' ), 8, True ) == ( StrToIp( '10.0.0.0' ), StrToIp( '10.255.255.255' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.0.0' ), 8 ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.255.255.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.0.0' ), 8, False ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.255.255.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.0.0' ), 8, True ) == ( StrToIp( '10.0.0.0' ), StrToIp( '10.255.255.255' ) )

  assert CIDRNetworkBounds( StrToIp( '10.0.0.0' ), 24 ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.0.0.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.0' ), 24, False ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.0.0.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.0' ), 24, True ) == ( StrToIp( '10.0.0.0' ), StrToIp( '10.0.0.255' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.1' ), 24 ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.0.0.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.1' ), 24, False ) == ( StrToIp( '10.0.0.1' ), StrToIp( '10.0.0.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.0.0.1' ), 24, True ) == ( StrToIp( '10.0.0.0' ), StrToIp( '10.0.0.255' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.0.0' ), 24 ) == ( StrToIp( '10.3.0.1' ), StrToIp( '10.3.0.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.0.0' ), 24, False ) == ( StrToIp( '10.3.0.1' ), StrToIp( '10.3.0.254' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.0.0' ), 24, True ) == ( StrToIp( '10.3.0.0' ), StrToIp( '10.3.0.255' ) )

  assert CIDRNetworkBounds( StrToIp( '2001::' ), 112 ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fffe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::' ), 112, False ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fffe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::' ), 112, True ) == ( StrToIp( '2001::' ), StrToIp( '2001::ffff' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::1' ), 112 ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fffe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::1' ), 112, False ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fffe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::1' ), 112, True ) == ( StrToIp( '2001::' ), StrToIp( '2001::ffff' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f001' ), 112 ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fffe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f001' ), 112, False ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fffe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f001' ), 112, True ) == ( StrToIp( '2001::' ), StrToIp( '2001::ffff' ) )

  assert CIDRNetworkBounds( StrToIp( '2001::' ), 120 ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::' ), 120, False ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::' ), 120, True ) == ( StrToIp( '2001::' ), StrToIp( '2001::ff' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::1' ), 120 ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::1' ), 120, False ) == ( StrToIp( '2001::1' ), StrToIp( '2001::fe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::1' ), 120, True ) == ( StrToIp( '2001::' ), StrToIp( '2001::ff' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f001' ), 120 ) == ( StrToIp( '2001::f001' ), StrToIp( '2001::f0fe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f001' ), 120, False ) == ( StrToIp( '2001::f001' ), StrToIp( '2001::f0fe' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f001' ), 120, True ) == ( StrToIp( '2001::f000' ), StrToIp( '2001::f0ff' ) )

  assert CIDRNetworkBounds( StrToIp( '10.3.2.5' ), 32 ) == ( StrToIp( '10.3.2.5' ), StrToIp( '10.3.2.5' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.2.5' ), 32, False ) == ( StrToIp( '10.3.2.5' ), StrToIp( '10.3.2.5' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.2.5' ), 32, True ) == ( StrToIp( '10.3.2.5' ), StrToIp( '10.3.2.5' ) )

  assert CIDRNetworkBounds( StrToIp( '10.3.2.5' ), 31 ) == ( StrToIp( '10.3.2.4' ), StrToIp( '10.3.2.5' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.2.5' ), 31, False ) == ( StrToIp( '10.3.2.4' ), StrToIp( '10.3.2.5' ) )
  assert CIDRNetworkBounds( StrToIp( '10.3.2.5' ), 31, True ) == ( StrToIp( '10.3.2.4' ), StrToIp( '10.3.2.5' ) )

  assert CIDRNetworkBounds( StrToIp( '2001::f009' ), 128 ) == ( StrToIp( '2001::f009' ), StrToIp( '2001::f009' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f009' ), 128, False ) == ( StrToIp( '2001::f009' ), StrToIp( '2001::f009' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f009' ), 128, True ) == ( StrToIp( '2001::f009' ), StrToIp( '2001::f009' ) )

  assert CIDRNetworkBounds( StrToIp( '2001::f009' ), 127 ) == ( StrToIp( '2001::f008' ), StrToIp( '2001::f009' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f009' ), 127, False ) == ( StrToIp( '2001::f008' ), StrToIp( '2001::f009' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::f009' ), 127, True ) == ( StrToIp( '2001::f008' ), StrToIp( '2001::f009' ) )

  assert CIDRNetworkBounds( StrToIp( '254.0.0.0' ), 8, True ) == ( StrToIp( '254.0.0.0' ), StrToIp( '254.255.255.255' ) )
  assert CIDRNetworkBounds( StrToIp( '255.0.0.0' ), 8, True ) == ( StrToIp( '255.0.0.0' ), StrToIp( '255.255.255.255' ) )
  assert CIDRNetworkBounds( StrToIp( '1.2.3.4' ), 0, True ) == ( StrToIp( '0.0.0.0' ), StrToIp( '255.255.255.255' ) )
  assert CIDRNetworkBounds( StrToIp( '2001::' ), 0, True ) == ( StrToIp( '::' ), StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff' ) )

  with pytest.raises( ValueError ):
    CIDRNetworkBounds( -1, 0 )
  with pytest.raises( ValueError ):
    CIDRNetworkBounds( 0x100000000000000000000000000000000, 0 )
  with pytest.raises( ValueError ):
    CIDRNetworkBounds( StrToIp( '255.255.255.255' ), 33 )
  with pytest.raises( ValueError ):
    CIDRNetworkBounds( StrToIp( '0.0.0.0' ), 33 )
  with pytest.raises( ValueError ):
    CIDRNetworkBounds( StrToIp( 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff' ), 129 )
  with pytest.raises( ValueError ):
    CIDRNetworkBounds( StrToIp( '::' ), 129 )
  with pytest.raises( ValueError ):
    CIDRNetworkBounds( '::', 129 )


def test_cidrnetworkrange():
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 32 ) ) == [ StrToIp( '169.254.1.3' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 32, True ) ) == [ StrToIp( '169.254.1.3' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 32, False ) ) == [ StrToIp( '169.254.1.3' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 31 ) ) == [ StrToIp( '169.254.1.2' ), StrToIp( '169.254.1.3' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 31, True ) ) == [ StrToIp( '169.254.1.2' ), StrToIp( '169.254.1.3' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 31, False ) ) == [ StrToIp( '169.254.1.2' ), StrToIp( '169.254.1.3' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 30 ) ) == [ StrToIp( '169.254.1.1' ), StrToIp( '169.254.1.2' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 30, True ) ) == [ StrToIp( '169.254.1.0' ), StrToIp( '169.254.1.1' ), StrToIp( '169.254.1.2' ), StrToIp( '169.254.1.3' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 30, False ) ) == [ StrToIp( '169.254.1.1' ), StrToIp( '169.254.1.2' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 29 ) ) == [ StrToIp( '169.254.1.1' ), StrToIp( '169.254.1.2' ), StrToIp( '169.254.1.3' ), StrToIp( '169.254.1.4' ), StrToIp( '169.254.1.5' ), StrToIp( '169.254.1.6' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 29, True ) ) == [ StrToIp( '169.254.1.0' ), StrToIp( '169.254.1.1' ), StrToIp( '169.254.1.2' ), StrToIp( '169.254.1.3' ), StrToIp( '169.254.1.4' ), StrToIp( '169.254.1.5' ), StrToIp( '169.254.1.6' ), StrToIp( '169.254.1.7' ) ]
  assert list( CIDRNetworkRange( StrToIp( '169.254.1.3' ), 29, False ) ) == [ StrToIp( '169.254.1.1' ), StrToIp( '169.254.1.2' ), StrToIp( '169.254.1.3' ), StrToIp( '169.254.1.4' ), StrToIp( '169.254.1.5' ), StrToIp( '169.254.1.6' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 128 ) ) == [ StrToIp( '2::5' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 128, True ) ) == [ StrToIp( '2::5' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 128, False ) ) == [ StrToIp( '2::5' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 127 ) ) == [ StrToIp( '2::4' ), StrToIp( '2::5' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 127, True ) ) == [ StrToIp( '2::4' ), StrToIp( '2::5' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 127, False ) ) == [ StrToIp( '2::4' ), StrToIp( '2::5' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 126 ) ) == [ StrToIp( '2::5' ), StrToIp( '2::6' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 126, True ) ) == [ StrToIp( '2::4' ), StrToIp( '2::5' ), StrToIp( '2::6' ), StrToIp( '2::7' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 126, False ) ) == [ StrToIp( '2::5' ), StrToIp( '2::6' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 125 ) ) == [ StrToIp( '2::1' ), StrToIp( '2::2' ), StrToIp( '2::3' ), StrToIp( '2::4' ), StrToIp( '2::5' ), StrToIp( '2::6' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 125, True ) ) == [ StrToIp( '2::0' ), StrToIp( '2::1' ), StrToIp( '2::2' ), StrToIp( '2::3' ), StrToIp( '2::4' ), StrToIp( '2::5' ), StrToIp( '2::6' ), StrToIp( '2::7' ) ]
  assert list( CIDRNetworkRange( StrToIp( '2::5' ), 125, False ) ) == [ StrToIp( '2::1' ), StrToIp( '2::2' ), StrToIp( '2::3' ), StrToIp( '2::4' ), StrToIp( '2::5' ), StrToIp( '2::6' ) ]


def test_cidrnetworksizerange():  # NOTE: becarefull with the prefixes here, this can generate some pretty large networks even a /8 in ipv4 can make this test take a while
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 32 ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 32 ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 32, True ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 32, True ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 32, False ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 32, False ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 31 ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 31 ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 31, True ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 31, True ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 31, False ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 31, False ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 30 ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 30 ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 30, True ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 30, True ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 30, False ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 30, False ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 16 ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 16 ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 16, True ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 16, True ) ) )
  assert CIDRNetworkSize( StrToIp( '34.54.23.12' ), 16, False ) == len( list( CIDRNetworkRange( StrToIp( '34.54.23.12' ), 16, False ) ) )

  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 128 ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 128 ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 128, True ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 128, True ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 128, False ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 128, False ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 127 ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 127 ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 127, True ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 127, True ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 127, False ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 127, False ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 126 ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 126 ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 126, True ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 126, True ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 126, False ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 126, False ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 125 ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 125 ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 125, True ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 125, True ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 125, False ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 125, False ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 124 ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 124 ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 124, True ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 124, True ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 124, False ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 124, False ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 120 ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 120 ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 120, True ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 120, True ) ) )
  assert CIDRNetworkSize( StrToIp( '1:2:3::' ), 120, False ) == len( list( CIDRNetworkRange( StrToIp( '1:2:3::' ), 120, False ) ) )
