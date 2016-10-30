from ip import StrToIp

def test_strtoip():
  ip = StrToIp( '127.0.0.1' )
  assert ip == 0

  ip = StrToIp( '::1' )
  assert ip == 0

  # also test ::
  # also tes ipv4 detection
  # make sure calls are not modifying the value passed in
