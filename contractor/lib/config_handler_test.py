import pytest

from contractor.Site.models import Site
from contractor.Utilities.models import AddressBlock, Address, RealNetworkInterface
from contractor.BluePrint.models import FoundationBluePrint, StructureBluePrint, PXE
from contractor.Building.models import Foundation, Structure
from contractor.lib.config_handler import url_regex, handler


def test_url_regex():
  assert url_regex.match( '' ) is None
  assert url_regex.match( 'config/config' ) is None
  assert url_regex.match( '/config' ) is None
  assert url_regex.match( '/config//1' ) is None
  assert url_regex.match( '/config//123' ) is None
  assert url_regex.match( '/config//a' ) is None
  assert url_regex.match( '/config/234/1' ) is None
  assert url_regex.match( '/config/234/00000000-0000-4000-0000-000000000000' ) is None
  assert url_regex.match( '/config/234/locator' ) is None
  assert url_regex.match( '/config/234/s/1' ) is None
  assert url_regex.match( '/config/234/c/00000000-0000-4000-0000-000000000000' ) is None
  assert url_regex.match( '/config/234/f/locator' ) is None
  assert url_regex.match( '/config/config/1' ) is None
  assert url_regex.match( '/config/config/00000000-0000-4000-0000-000000000000' ) is None
  assert url_regex.match( '/config/config/locator' ) is None

  assert url_regex.match( '/config/config/' ).groups() == ( 'config', None, None, None, None )
  assert url_regex.match( '/config/boot_script/' ).groups() == ( 'boot_script', None, None, None, None )
  assert url_regex.match( '/config/pxe_template/' ).groups() == ( 'pxe_template', None, None, None, None )

  assert url_regex.match( '/config/config/s/00000000-0000-4000-0000-000000000000' ) is None
  assert url_regex.match( '/config/config/s/locator' ) is None
  assert url_regex.match( '/config/config/s/1' ).groups() == ( 'config', 's/1', None, 's/1', None )
  assert url_regex.match( '/config/config/s/sdf' ) is None
  assert url_regex.match( '/config/config/s/234' ).groups() == ( 'config', 's/234', None, 's/234', None )
  assert url_regex.match( '/config/config/s/2d3' ) is None

  assert url_regex.match( '/config/config/c/123' ) is None
  assert url_regex.match( '/config/config/c/locator' ) is None
  assert url_regex.match( '/config/config/c/123-123' ) is None
  assert url_regex.match( '/config/config/c/00000000-0000-4000-0000-000000000000' ).groups() == ( 'config', 'c/00000000-0000-4000-0000-000000000000', 'c/00000000-0000-4000-0000-000000000000', None, None )
  assert url_regex.match( '/config/config/c/085de71d-9123-45ef-8322-93fa3d1cacea' ).groups() == ( 'config', 'c/085de71d-9123-45ef-8322-93fa3d1cacea', 'c/085de71d-9123-45ef-8322-93fa3d1cacea', None, None )
  assert url_regex.match( '/config/config/c/085de71d-9123-45ef-8322-93fa3d1cacea/' ) is None

  assert url_regex.match( '/config/config/f/12' ).groups() == ( 'config', 'f/12', None, None, 'f/12' )
  assert url_regex.match( '/config/config/f/00000000-0000-4000-0000-000000000000' ).groups() == ( 'config', 'f/00000000-0000-4000-0000-000000000000', None, None, 'f/00000000-0000-4000-0000-000000000000' )
  assert url_regex.match( '/config/config/f/locator' ).groups() == ( 'config', 'f/locator', None, None, 'f/locator' )
  assert url_regex.match( '/config/config/f/something-really_fancy' ).groups() == ( 'config', 'f/something-really_fancy', None, None, 'f/something-really_fancy' )
  assert url_regex.match( '/config/config/f/n00b' ).groups() == ( 'config', 'f/n00b', None, None, 'f/n00b' )


class Request:
  def __init__( self, uri, remote_addr ):
    self.uri = uri
    self.remote_addr = remote_addr


def _test_dict( target, reference ):
  for key in reference:
    assert target[ key ] == reference[ key ], key


@pytest.mark.django_db
def test_handler():
  s = Site( name='test', description='test site' )
  s.full_clean()
  s.save()

  ab = AddressBlock( name='test', site=s, subnet='10.0.0.0', gateway_offset=1, prefix=24 )
  ab.full_clean()
  ab.save()

  fbp = FoundationBluePrint( name='fdn_test', description='foundation test bp' )
  fbp.foundation_type_list = 'Unknown'
  fbp.full_clean()
  fbp.save()

  sbp = StructureBluePrint( name='str_test', description='structure test bp' )
  sbp.full_clean()
  sbp.save()
  sbp.foundation_blueprint_list.add( fbp )

  pxe = PXE( name='testpxe', boot_script='boot', template='this is for the testing' )
  pxe.full_clean()
  pxe.save()

  fdn = Foundation( locator='ftester', blueprint=fbp, site=s )
  fdn.full_clean()
  fdn.save()

  iface = RealNetworkInterface( name='eth0', is_provisioning=True )
  iface.foundation = fdn
  iface.physical_location = 'eth0'
  iface.full_clean()
  iface.save()

  str = Structure( hostname='stester', foundation=fdn, blueprint=sbp, site=s )
  str.full_clean()
  str.save()
  str.config_uuid = '8b6663f9-efa8-467c-b973-ac79e66e3c78'
  str.save()

  addr = Address( networked=str, address_block=ab, interface_name='eth0', offset=5, is_primary=True )
  addr.full_clean()
  addr.save()

  assert handler( Request( '', None ) ).http_code == 400
  assert handler( Request( '/config/config', None ) ).http_code == 400
  assert handler( Request( '/config/234/', None ) ).http_code == 400
  assert handler( Request( '/config/config/', '127.0.0.1' ) ).http_code == 404
  with pytest.raises( ValueError ):
    handler( Request( '/config/config/', None ) )

  assert handler( Request( '/config/config/s/1000', None ) ).http_code == 404
  assert handler( Request( '/config/config/f/test', None ) ).http_code == 404
  assert handler( Request( '/config/config/c/00000000-0000-4000-0000-000000000000', None ) ).http_code == 404

  assert handler( Request( '/config/config/s/asdf', None ) ).http_code == 400
  assert handler( Request( '/config/config/c/00000000-0000-4000-0000-00000', None ) ).http_code == 400

  assert handler( Request( '/config/config/', '10.0.0.1' ) ).http_code == 404

  resp = handler( Request( '/config/config/', '10.0.0.5' ) )
  assert resp.http_code == 200
  _test_dict( resp.data, {
                            '_blueprint': 'str_test',
                            '_foundation_id': 'ftester',
                            '_foundation_locator': 'ftester',
                            '_foundation_state': 'planned',
                            '_foundation_type': 'Unknown',
                            '_fqdn': 'stester',
                            '_hostname': 'stester',
                            '_structure_config_uuid': '8b6663f9-efa8-467c-b973-ac79e66e3c78'
                          } )

  resp = handler( Request( '/config/config/s/5', None ) )
  assert resp.http_code == 200
  _test_dict( resp.data, {
                            '_blueprint': 'str_test',
                            '_foundation_id': 'ftester',
                            '_foundation_locator': 'ftester',
                            '_foundation_state': 'planned',
                            '_foundation_type': 'Unknown',
                            '_fqdn': 'stester',
                            '_hostname': 'stester',
                            '_structure_config_uuid': '8b6663f9-efa8-467c-b973-ac79e66e3c78',
                          } )

  resp = handler( Request( '/config/config/c/8b6663f9-efa8-467c-b973-ac79e66e3c78', None ) )
  assert resp.http_code == 200
  _test_dict( resp.data, {
                            '_blueprint': 'str_test',
                            '_foundation_id': 'ftester',
                            '_foundation_locator': 'ftester',
                            '_foundation_state': 'planned',
                            '_foundation_type': 'Unknown',
                            '_fqdn': 'stester',
                            '_hostname': 'stester',
                            '_structure_config_uuid': '8b6663f9-efa8-467c-b973-ac79e66e3c78',
                          } )

  resp = handler( Request( '/config/config/f/ftester', None ) )
  assert resp.http_code == 200
  _test_dict( resp.data, {
                            '_blueprint': 'fdn_test',
                            '_foundation_id': 'ftester',
                            '_foundation_locator': 'ftester',
                            '_foundation_state': 'planned',
                            '_foundation_type': 'Unknown',
                          } )

  resp = handler( Request( '/config/pxe_template/', '10.0.0.5' ) )
  assert resp.http_code == 200
  assert resp.data == ''

  resp = handler( Request( '/config/boot_script/', '10.0.0.5' ) )
  assert resp.http_code == 200
  assert resp.data == ''

  iface.pxe = pxe
  iface.full_clean()
  iface.save()

  resp = handler( Request( '/config/pxe_template/', '10.0.0.5' ) )
  assert resp.http_code == 200
  assert resp.data == 'this is for the testing'

  resp = handler( Request( '/config/boot_script/', '10.0.0.5' ) )
  assert resp.http_code == 200
  assert resp.data == '#!ipxe\n\nboot'
