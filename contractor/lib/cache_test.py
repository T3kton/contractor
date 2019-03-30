import pytest

from contractor.Site.models import Site
from contractor.Building.models import Structure, Foundation
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint
from contractor.lib.cache import _collection, removeConfig


fake_key = None
fake_item = None


def _tweek_variables( value ):
  for i in ( '__last_modified', '__timestamp' ):
    if i in value:
      value[ i ] = '*DATETIME*'

  for i in ( '_structure_config_uuid', ):
    if i in value:
      value[ i ] = '*UUID*'

  for i in ( '_structure_id', ):
    if i in value:
      value[ i ] = '*ID*'

  return value


class FakeCollection():
  def __init__( self, name ):
    self.name = name

  def update( self, key, item, upsert ):
    global fake_key
    global fake_item

    assert upsert is True
    fake_key = key
    fake_item = item


class FakeDB():
  site = FakeCollection( 'Site' )
  blueprint = FakeCollection( 'BluePrint' )
  structure = FakeCollection( 'Structure' )
  foundation = FakeCollection( 'Foundation' )


def fake_connect():
  return FakeDB()


def test_collection():
  db = fake_connect()

  t = Site()
  assert _collection( db, t ).name == 'Site'

  t = Structure()
  assert _collection( db, t ).name == 'Structure'

  t = Foundation()
  assert _collection( db, t ).name == 'Foundation'

  t = StructureBluePrint()
  assert _collection( db, t ).name == 'BluePrint'

  t = FoundationBluePrint()
  assert _collection( db, t ).name == 'BluePrint'


@pytest.mark.django_db
def test_updateConfig_site( mocker ):
  mocker.patch( 'contractor.lib.cache._connect', fake_connect )
  global fake_key
  global fake_item

  fake_key = None
  fake_item = None
  s = Site()
  s.name = '1234test'
  s.description = 'test desc'
  s.full_clean()
  s.save()

  assert fake_key == { '_id': '1234test' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_site': '1234test'
                      }

  fake_key = None
  fake_item = None
  s.config_values = { 'a': 42, 'z': 'abc' }
  s.full_clean()
  s.save()

  assert fake_key == { '_id': '1234test' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_site': '1234test',
                        'a': 42,
                        'z': 'abc'
                      }


@pytest.mark.django_db
def test_updateConfig_blueprint( mocker ):
  mocker.patch( 'contractor.lib.cache._connect', fake_connect )
  global fake_key
  global fake_item

  fake_key = None
  fake_item = None
  sb = StructureBluePrint()
  sb.name = 'sbptest'
  sb.description = 'testing SBP'
  sb.full_clean()
  sb.save()

  assert fake_key == { '_id': 'sbptest' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_blueprint': 'sbptest'
                      }

  fake_key = None
  fake_item = None
  sb.config_values = { 'er': 'bob', 'um': 'sally' }
  sb.full_clean()
  sb.save()

  assert fake_key == { '_id': 'sbptest' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_blueprint': 'sbptest',
                        'er': 'bob',
                        'um': 'sally'
                      }

  fake_key = None
  fake_item = None
  fb = FoundationBluePrint()
  fb.name = 'fdntest'
  fb.description = 'testing FBP'
  fb.foundation_type_list = [ 'nope' ]
  fb.full_clean()
  fb.save()

  assert fake_key == { '_id': 'fdntest' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_blueprint': 'fdntest'
                      }

  fake_key = None
  fake_item = None
  fb.config_values = { 'qwert': [ 1, 2, 3, 'z' ] }
  fb.full_clean()
  fb.save()

  assert fake_key == { '_id': 'fdntest' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_blueprint': 'fdntest',
                        'qwert': [ 1, 2, 3, 'z' ]
                      }

  fake_key = None
  fake_item = None
  sb.foundation_blueprint_list = [ fb ]
  sb.full_clean()
  sb.save()

  assert fake_key == { '_id': 'sbptest' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_blueprint': 'sbptest',
                        'er': 'bob',
                        'um': 'sally'
                      }


@pytest.mark.django_db
def test_updateConfig_foundation( mocker ):
  mocker.patch( 'contractor.lib.cache._connect', fake_connect )
  global fake_key
  global fake_item

  s = Site()
  s.name = 'site_test'
  s.description = 'testing Site'
  s.full_clean()
  s.save()

  fb = FoundationBluePrint()
  fb.name = 'fdnbp_test'
  fb.description = 'testing FBP'
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  fake_key = None
  fake_item = None
  fdn = Foundation()
  fdn.locator = 'bobmachine'
  fdn.blueprint = fb
  fdn.site = s
  fdn.full_clean()
  fdn.save()

  assert fake_key == { '_id': 'bobmachine' }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_site': 'site_test',
                        '_blueprint': 'fdnbp_test',
                        '_foundation_class_list': [],
                        '_foundation_id': 'bobmachine',
                        '_foundation_interface_list': [],
                        '_foundation_locator': 'bobmachine',
                        '_foundation_state': 'planned',
                        '_foundation_type': 'Unknown'
                      }


@pytest.mark.django_db
def test_updateConfig_structure( mocker ):
  mocker.patch( 'contractor.lib.cache._connect', fake_connect )
  global fake_key
  global fake_item

  s = Site()
  s.name = 'site_test'
  s.description = 'testing Site'
  s.full_clean()
  s.save()

  fb = FoundationBluePrint()
  fb.name = 'fdnbp_test'
  fb.description = 'testing FBP'
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  fdn = Foundation()
  fdn.locator = 'fdn_test'
  fdn.blueprint = fb
  fdn.site = s
  fdn.full_clean()
  fdn.save()

  sb = StructureBluePrint()
  sb.name = 'strbp_test'
  sb.description = 'testing SBP'
  sb.full_clean()
  sb.save()

  sb.foundation_blueprint_list = [ fb ]
  sb.full_clean()
  sb.save()

  fake_key = None
  fake_item = None
  str = Structure()
  str.hostname = 'testme'
  str.site = s
  str.blueprint = sb
  str.foundation = fdn
  str.full_clean()
  str.save()

  # assert fake_key == { '_id': 1 }  # the auto inc value could be all sorts of values
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_site': 'site_test',
                        '_blueprint': 'strbp_test',
                        '_foundation_class_list': [],
                        '_foundation_id': 'fdn_test',
                        '_foundation_interface_list': [],
                        '_foundation_locator': 'fdn_test',
                        '_foundation_state': 'planned',
                        '_foundation_type': 'Unknown',
                        '_fqdn': 'testme',
                        '_hostname': 'testme',
                        '_interface_map': {},
                        '_provisioning_interface': None,
                        '_provisioning_interface_mac': None,
                        '_structure_config_uuid': '*UUID*',
                        '_structure_id': '*ID*',
                        '_structure_state': 'planned'
                      }

  fake_key = None
  fake_item = None
  str.config_values = { 'sdf': { 'a': 'rrrr', 'b': [ 1, 2, 3, 4 ] } }
  str.full_clean()
  str.save()

  # assert fake_key == { '_id': 1 }
  assert _tweek_variables( fake_item ) == {
                        '__last_modified': '*DATETIME*',
                        '__timestamp': '*DATETIME*',
                        '_site': 'site_test',
                        '_blueprint': 'strbp_test',
                        '_foundation_class_list': [],
                        '_foundation_id': 'fdn_test',
                        '_foundation_interface_list': [],
                        '_foundation_locator': 'fdn_test',
                        '_foundation_state': 'planned',
                        '_foundation_type': 'Unknown',
                        '_fqdn': 'testme',
                        '_hostname': 'testme',
                        '_interface_map': {},
                        '_provisioning_interface': None,
                        '_provisioning_interface_mac': None,
                        '_structure_config_uuid': '*UUID*',
                        '_structure_id': '*ID*',
                        '_structure_state': 'planned',
                        'sdf': { 'a': 'rrrr', 'b': [ 1, 2, 3, 4 ] }
                      }
