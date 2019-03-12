import pytest
from datetime import datetime, timedelta, timezone
from django.core.exceptions import ValidationError

from contractor.Site.models import Site
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint
from contractor.Building.models import Foundation, Structure
from contractor.lib.config import _updateConfig, mergeValues, getConfig, renderTemplate


def test_string():
  config = {}
  _updateConfig( {}, [], config )
  assert config == {}

  _updateConfig( { 'bob': '1 adsf' }, [], config )
  assert config == { 'bob': '1 adsf' }

  _updateConfig( { '<bob': '1 ' }, [], config )
  assert config == { 'bob': '1 1 adsf' }

  _updateConfig( { '>bob': ' 8' }, [], config )
  assert config == { 'bob': '1 1 adsf 8' }

  _updateConfig( { '>bob': [ 9 ] }, [], config )
  assert config == { 'bob': '1 1 adsf 8[9]' }

  _updateConfig( { '>bob': { 'a': 99 } }, [], config )
  assert config == { 'bob': "1 1 adsf 8[9]{'a': 99}" }

  _updateConfig( { '-bob': "{'a': 99}" }, [], config )
  assert config == { 'bob': '1 1 adsf 8[9]' }

  _updateConfig( { '-bob': '1 ' }, [], config )
  assert config == { 'bob': '1 adsf 8[9]' }

  _updateConfig( { '-bob': 'zzz' }, [], config )
  assert config == { 'bob': '1 adsf 8[9]' }

  _updateConfig( { 'bob': 'zzz' }, [], config )
  assert config == { 'bob': 'zzz' }

  _updateConfig( { '~bob': 'zzz' }, [], config )
  assert config == {}

  _updateConfig( { '~bob': 'zzz' }, [], config )
  assert config == {}

  _updateConfig( { '<bob': '1' }, [], config )
  assert config == { 'bob': '1' }

  _updateConfig( { '~bob': 'zzz' }, [], config )
  assert config == {}

  _updateConfig( { '<bob': '2' }, [], config )
  assert config == { 'bob': '2' }


def test_list():
  config = {}
  _updateConfig( {}, [], config )
  assert config == {}

  _updateConfig( { 'bob': [ 1, 2, 2 ] }, [], config )
  assert config == { 'bob': [ 1, 2, 2 ] }

  _updateConfig( { '<bob': [ 0 ] }, [], config )
  assert config == { 'bob': [ 0, 1, 2, 2 ] }

  _updateConfig( { '<bob': 0 }, [], config )
  assert config == { 'bob': [ 0, 0, 1, 2, 2 ] }

  _updateConfig( { '>bob': [ 7, 8 ] }, [], config )
  assert config == { 'bob': [ 0, 0, 1, 2, 2, 7, 8 ] }

  _updateConfig( { '>bob': 9 }, [], config )
  assert config == { 'bob': [ 0, 0, 1, 2, 2, 7, 8, 9 ] }

  _updateConfig( { '<bob': { 's': '***' } }, [], config )
  assert config == { 'bob': [ { 's': '***' }, 0, 0, 1, 2, 2, 7, 8, 9 ] }

  _updateConfig( { '-bob': { 's': '***' } }, [], config )
  assert config == { 'bob': [ 0, 0, 1, 2, 2, 7, 8, 9 ] }

  _updateConfig( { '-bob': [ 7 ] }, [], config )
  assert config == { 'bob': [ 0, 0, 1, 2, 2, 8, 9 ] }

  _updateConfig( { '-bob': [ 1, 2 ] }, [], config )
  assert config == { 'bob': [ 0, 0, 2, 8, 9 ] }

  _updateConfig( { '-bob': [ 1, 2 ] }, [], config )
  assert config == { 'bob': [ 0, 0, 8, 9 ] }

  _updateConfig( { '-bob': 9 }, [], config )
  assert config == { 'bob': [ 0, 0, 8 ] }

  _updateConfig( { '-bob': 9 }, [], config )
  assert config == { 'bob': [ 0, 0, 8 ] }

  _updateConfig( { 'bob': [ 'zzz' ] }, [], config )
  assert config == { 'bob': [ 'zzz' ] }

  _updateConfig( { '~bob': [ 'zzz' ] }, [], config )
  assert config == {}

  _updateConfig( { '~bob': [ 'zzz' ] }, [], config )
  assert config == {}

  _updateConfig( { '<bob': [ 'a', 'b' ] }, [], config )
  assert config == { 'bob': [ 'a', 'b' ] }

  _updateConfig( { '~bob': [ 'zzz' ] }, [], config )
  assert config == {}

  _updateConfig( { '>bob': [ 'y', 'z' ] }, [], config )
  assert config == { 'bob': [ 'y', 'z' ] }


def test_dict():
  config = {}
  _updateConfig( {}, [], config )
  assert config == {}

  _updateConfig( { 'bob': { 'a': 1, 'b': 2 } }, [], config )
  assert config == { 'bob': { 'a': 1, 'b': 2 }  }

  _updateConfig( { '<bob': { 'c': '3' } }, [], config )
  assert config == { 'bob': { 'a': 1, 'b': 2, 'c': '3' } }

  with pytest.raises( ValueError ):
    _updateConfig( { '<bob': 'asdf' }, [], config )

  with pytest.raises( ValueError ):
    _updateConfig( { '<bob': [ 'asdf' ] }, [], config )

  _updateConfig( { '>bob': { 'd': '4' } }, [], config )
  assert config == { 'bob': { 'a': 1, 'b': 2, 'c': '3', 'd': '4' } }

  with pytest.raises( ValueError ):
    _updateConfig( { '>bob': 'asdf' }, [], config )

  with pytest.raises( ValueError ):
    _updateConfig( { '>bob': [ 'asdf' ] }, [], config )

  _updateConfig( { '-bob': 'd' }, [], config )
  assert config == { 'bob': { 'a': 1, 'b': 2, 'c': '3' } }

  _updateConfig( { '-bob': 'd' }, [], config )
  assert config == { 'bob': { 'a': 1, 'b': 2, 'c': '3' } }

  _updateConfig( { '-bob': [ 'b', 'c' ] }, [], config )
  assert config == { 'bob': { 'a': 1 } }

  _updateConfig( { '-bob': [ 'b', 'c' ] }, [], config )
  assert config == { 'bob': { 'a': 1 } }

  _updateConfig( { '~bob': { 'z': 'zzz' } }, [], config )
  assert config == {}

  _updateConfig( { '~bob': { 'z': 'zzz' } }, [], config )
  assert config == {}

  _updateConfig( { '<bob': { 'a': 'aaa' } }, [], config )
  assert config == { 'bob': { 'a': 'aaa' } }

  _updateConfig( { '~bob': { 'z': 'zzz' } }, [], config )
  assert config == {}

  _updateConfig( { '<bob': { 'b': 'bbb' } }, [], config )
  assert config == { 'bob': { 'b': 'bbb' } }


def test_class():
  config = {}
  _updateConfig( {}, [], config )
  assert config == {}

  _updateConfig( { 'bob': 'adsf' }, [], config )
  assert config == { 'bob': 'adsf' }

  _updateConfig( { 'jane:joe': 'qwert' }, [], config )
  assert config == { 'bob': 'adsf' }

  _updateConfig( { 'jane:joe': 'qwert' }, [ 'joe' ], config )
  assert config == { 'bob': 'adsf', 'jane': 'qwert' }

  _updateConfig( { '<bob:joe': '1' }, [], config )
  assert config == { 'bob': 'adsf', 'jane': 'qwert' }

  _updateConfig( { '<bob:joe': '1' }, [ 'joe' ], config )
  assert config == { 'bob': '1adsf', 'jane': 'qwert' }


def test_mergeValues():
  values = { 'a': 'c' }
  assert { 'a': 'c' } == mergeValues( values )
  assert { 'a': 'c' } == values

  values = { 'a': 3 }
  assert { 'a': 3 } == mergeValues( values )
  assert { 'a': 3 } == values

  values = { 'a': 3, 'b': { 'c': 3 } }
  assert { 'a': 3, 'b': { 'c': 3 } } == mergeValues( values )
  assert { 'a': 3, 'b': { 'c': 3 } } == values

  values = { 'a': 3, 'b': [ 1, '3', 2 ] }
  assert { 'a': 3, 'b': [ 1, '3', 2 ] } == mergeValues( values )
  assert { 'a': 3, 'b': [ 1, '3', 2 ] } == values

  values = { 'a': 'c', 'd': '{{a}}' }
  assert { 'a': 'c', 'd': 'c' } == mergeValues( values )
  assert { 'a': 'c', 'd': '{{a}}' } == values

  values = { 'a': 1, 'd': '{{a}}', 'e': '"{{a}}"' }
  assert { 'a': 1, 'd': '1', 'e': '"1"' } == mergeValues( values )
  assert { 'a': 1, 'd': '{{a}}', 'e': '"{{a}}"' } == values

  values = { 'a': 'c', 'd': '{{ a }}' }
  assert { 'a': 'c', 'd': 'c' } == mergeValues( values )
  assert { 'a': 'c', 'd': '{{ a }}' } == values

  values = { 'a': 'c', 'd': '{{z|default(\'v\')}}' }
  assert { 'a': 'c', 'd': 'v' } == mergeValues( values )
  assert { 'a': 'c', 'd': '{{z|default(\'v\')}}' } == values

  values = { 'a': 'c', 'd': '{{a|default(\'v\')}}' }
  assert { 'a': 'c', 'd': 'c' } == mergeValues( values )
  assert { 'a': 'c', 'd': '{{a|default(\'v\')}}' } == values

  values = { 'a': 'c', 'd': { 'bob': 'sdf', 'sally': '{{a}}' } }
  assert { 'a': 'c', 'd': { 'bob': 'sdf', 'sally': 'c' } } == mergeValues( values )
  assert { 'a': 'c', 'd': { 'bob': 'sdf', 'sally': '{{a}}' } } == values

  values = { 'a': 'c', 'b': 'f', 'd': [ '{{a}}', '{{b}}', '{{a}}' ] }
  assert { 'a': 'c', 'b': 'f', 'd': [ 'c', 'f', 'c' ] } == mergeValues( values )
  assert { 'a': 'c', 'b': 'f', 'd': [ '{{a}}', '{{b}}', '{{a}}' ] } == values

  values = { 'zone': 'local', 'dns_search': [ 'bob.{{zone}}', '{{zone}}' ], 'fqdn': 'mybox.{{zone}}' }
  assert { 'zone': 'local', 'dns_search': [ 'bob.local', 'local' ], 'fqdn': 'mybox.local' } == mergeValues( values )
  assert { 'zone': 'local', 'dns_search': [ 'bob.{{zone}}', '{{zone}}' ], 'fqdn': 'mybox.{{zone}}' } == values

  # make sure we are not crossing item boundires
  values = { 'a': '{', 'b': '{a', 'c': '{', 'd': '{', 'e': '}}' }
  assert { 'a': '{', 'b': '{a', 'c': '{', 'd': '{', 'e': '}}' } == mergeValues( values )
  assert { 'a': '{', 'b': '{a', 'c': '{', 'd': '{', 'e': '}}' } == values

  values = { 'a': 'c', 'b': 'a', 'd': '{{ "{{" }}{{b}}}}' }
  assert { 'a': 'c', 'b': 'a', 'd': 'c' } == mergeValues( values )
  assert { 'a': 'c', 'b': 'a', 'd': '{{ "{{" }}{{b}}}}' } == values


def test_render():
  assert renderTemplate( 'This is a test', {} ) == 'This is a test'

  config = { 'i': 'is only' }
  assert renderTemplate( 'This {{i}} {{j|default(\'a\')}} test', config ) == 'This is only a test'

  assert renderTemplate( 'This {{i}} {{j}} test', config ) == 'This is only  test'


def _strip_base( value ):
  for i in ( '__contractor_host', '__pxe_location', '__pxe_template_location', '__last_modified', '__timestamp', '_structure_config_uuid' ):
    try:
      del value[ i ]
    except KeyError:
      pass

  return value


@pytest.mark.django_db
def test_valid_names():
  s1 = Site( name='site1', description='test site 1' )
  s1.full_clean()
  s1.save()

  s1.config_values[ 'valid' ] = 'value 1'
  s1.full_clean()

  s1.config_values[ '_nope' ] = 'more value 1'
  with pytest.raises( ValidationError ):
    s1.full_clean()

  s1 = Site.objects.get( name='site1' )
  s1.full_clean()

  s1.config_values[ '__bad' ] = 'bad bad bad 1'
  with pytest.raises( ValidationError ):
    s1.full_clean()

  fb1 = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb1.foundation_type_list = [ 'Unknown' ]
  fb1.full_clean()
  fb1.save()

  fb1.config_values[ 'valid' ] = 'value 2'
  fb1.full_clean()

  fb1.config_values[ '_nope' ] = 'more value 2'
  with pytest.raises( ValidationError ):
    fb1.full_clean()

  fb1 = FoundationBluePrint.objects.get( pk='fdnb1' )
  fb1.full_clean()

  fb1.config_values[ '__bad' ] = 'bad bad bad 2'
  with pytest.raises( ValidationError ):
    fb1.full_clean()

  fb1 = FoundationBluePrint.objects.get( pk='fdnb1' )
  fb1.full_clean()

  sb1 = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb1.full_clean()
  sb1.save()
  sb1.foundation_blueprint_list.add( fb1 )

  sb1.config_values[ 'valid' ] = 'value 3'
  sb1.full_clean()

  sb1.config_values[ '_nope' ] = 'more value 3'
  with pytest.raises( ValidationError ):
    sb1.full_clean()

  sb1 = StructureBluePrint.objects.get( name='strb1' )
  sb1.full_clean()

  sb1.config_values[ '__bad' ] = 'bad bad bad 3'
  with pytest.raises( ValidationError ):
    sb1.full_clean()

  f1 = Foundation( site=s1, locator='fdn1', blueprint=fb1 )
  f1.full_clean()
  f1.save()

  str1 = Structure( foundation=f1, site=s1, hostname='struct1', blueprint=sb1 )
  str1.full_clean()
  str1.save()

  str1.config_values[ 'valid' ] = 'value 4'
  str1.full_clean()

  str1.config_values[ '_nope' ] = 'more value 4'
  with pytest.raises( ValidationError ):
    str1.full_clean()

  str1 = Structure.objects.get( hostname='struct1' )
  str1.full_clean()

  str1.config_values[ '__bad' ] = 'bad bad bad 4'
  with pytest.raises( ValidationError ):
    str1.full_clean()


def test_getconfig():
  with pytest.raises( ValueError ):
    getConfig( object() )


@pytest.mark.django_db
def test_site():
  s1 = Site( name='site1', description='test site 1' )
  s1.config_values = {}
  s1.full_clean()
  s1.save()

  now = datetime.now( timezone.utc )
  tmp = getConfig( s1 )
  assert now - tmp[ '__last_modified' ] < timedelta( seconds=5 )
  assert now - tmp[ '__timestamp' ] < timedelta( seconds=5 )

  del tmp[ '__last_modified' ]
  del tmp[ '__timestamp' ]

  assert tmp == {
                  '__contractor_host': 'http://contractor/',
                  '__pxe_location': 'http://static/pxe/',
                  '__pxe_template_location': 'http://contractor/config/pxe_template/',
                  '_site': 'site1'
                }

  assert _strip_base( getConfig( s1 ) ) == {
                                               '_site': 'site1'
                                            }

  s2 = Site( name='site2', description='test site 2', parent=s1 )
  s2.config_values = { 'myval': 'this is a test', 'stuff': 'this is only a test' }
  s2.full_clean()
  s2.save()

  assert _strip_base( getConfig( s2 ) ) == {
                                               '_site': 'site2',
                                               'myval': 'this is a test',
                                               'stuff': 'this is only a test'
                                            }

  s1.config_values = { 'under': 'or over' }
  s1.full_clean()
  s1.save()

  assert _strip_base( getConfig( s2 ) ) == {
                                               '_site': 'site2',
                                               'myval': 'this is a test',
                                               'stuff': 'this is only a test',
                                               'under': 'or over'
                                            }

  s2.config_values[ '>under' ] = ' here'
  s2.config_values[ '<under' ] = 'going '
  s2.full_clean()
  s2.save()

  assert _strip_base( getConfig( s2 ) ) == {
                                               '_site': 'site2',
                                               'myval': 'this is a test',
                                               'stuff': 'this is only a test',
                                               'under': 'going or over here'
                                            }


@pytest.mark.django_db
def test_blueprint():
  fb1 = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb1.foundation_type_list = [ 'Unknown' ]
  fb1.full_clean()
  fb1.save()

  now = datetime.now( timezone.utc )
  tmp = getConfig( fb1 )
  assert now - tmp[ '__last_modified' ] < timedelta( seconds=5 )
  assert now - tmp[ '__timestamp' ] < timedelta( seconds=5 )

  del tmp[ '__last_modified' ]
  del tmp[ '__timestamp' ]

  assert tmp == {
                  '__contractor_host': 'http://contractor/',
                  '__pxe_location': 'http://static/pxe/',
                  '__pxe_template_location': 'http://contractor/config/pxe_template/',
                  '_blueprint': 'fdnb1'
                }

  assert _strip_base( getConfig( fb1 ) ) == {
                                              '_blueprint': 'fdnb1'
                                            }

  fb2 = FoundationBluePrint( name='fdnb2', description='Foundation BluePrint 2' )
  fb2.foundation_type_list = [ 'Unknown' ]
  fb2.config_values = { 'the': 'Nice value' }
  fb2.full_clean()
  fb2.save()
  fb2.parent_list.add( fb1 )

  assert _strip_base( getConfig( fb2 ) ) == {
                                              '_blueprint': 'fdnb2',
                                              'the': 'Nice value'
                                            }

  fb1.config_values = { 'from': 'inside the house' }
  fb1.full_clean()
  fb1.save()

  assert _strip_base( getConfig( fb2 ) ) == {
                                              '_blueprint': 'fdnb2',
                                              'the': 'Nice value',
                                              'from': 'inside the house'
                                            }

  sb1 = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb1.full_clean()
  sb1.save()

  now = datetime.now( timezone.utc )
  tmp = getConfig( sb1 )
  assert now - tmp[ '__last_modified' ] < timedelta( seconds=5 )
  assert now - tmp[ '__timestamp' ] < timedelta( seconds=5 )

  del tmp[ '__last_modified' ]
  del tmp[ '__timestamp' ]

  assert tmp == {
                  '__contractor_host': 'http://contractor/',
                  '__pxe_location': 'http://static/pxe/',
                  '__pxe_template_location': 'http://contractor/config/pxe_template/',
                  '_blueprint': 'strb1'
                }

  assert _strip_base( getConfig( sb1 ) ) == {
                                              '_blueprint': 'strb1'
                                            }

  sb2 = StructureBluePrint( name='strb2', description='Structure BluePrint 2' )
  sb2.full_clean()
  sb2.save()
  sb2.parent_list.add( sb1 )

  assert _strip_base( getConfig( sb2 ) ) == {
                                              '_blueprint': 'strb2'
                                            }

  sb2.foundation_blueprint_list.add( fb2 )

  assert _strip_base( getConfig( sb2 ) ) == {
                                              '_blueprint': 'strb2'
                                            }


@pytest.mark.django_db
def test_foundation():
  s1 = Site( name='site1', description='test site 1' )
  s1.config_values = {}
  s1.full_clean()
  s1.save()

  fb1 = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb1.foundation_type_list = [ 'Unknown' ]
  fb1.full_clean()
  fb1.save()

  f1 = Foundation( site=s1, locator='fdn1', blueprint=fb1 )
  f1.full_clean()
  f1.save()

  now = datetime.now( timezone.utc )
  tmp = getConfig( f1 )
  assert now - tmp[ '__last_modified' ] < timedelta( seconds=5 )
  assert now - tmp[ '__timestamp' ] < timedelta( seconds=5 )

  del tmp[ '__last_modified' ]
  del tmp[ '__timestamp' ]

  assert tmp == {
                  '__contractor_host': 'http://contractor/',
                  '__pxe_location': 'http://static/pxe/',
                  '__pxe_template_location': 'http://contractor/config/pxe_template/',
                  '_foundation_class_list': [],
                  '_foundation_id': 'fdn1',
                  '_foundation_interface_list': [],
                  '_foundation_locator': 'fdn1',
                  '_foundation_state': 'planned',
                  '_foundation_type': 'Unknown',
                  '_blueprint': 'fdnb1',
                  '_site': 'site1'
                }

  assert _strip_base( getConfig( f1 ) ) == {
                                            '_foundation_class_list': [],
                                            '_foundation_id': 'fdn1',
                                            '_foundation_interface_list': [],
                                            '_foundation_locator': 'fdn1',
                                            '_foundation_state': 'planned',
                                            '_foundation_type': 'Unknown',
                                            '_blueprint': 'fdnb1',
                                            '_site': 'site1'
                                           }

  fb1.config_values[ 'lucky' ] = 'blueprint'
  fb1.full_clean()
  fb1.save()

  assert _strip_base( getConfig( f1 ) ) == {
                                            '_foundation_class_list': [],
                                            '_foundation_id': 'fdn1',
                                            '_foundation_interface_list': [],
                                            '_foundation_locator': 'fdn1',
                                            '_foundation_state': 'planned',
                                            '_foundation_type': 'Unknown',
                                            '_blueprint': 'fdnb1',
                                            '_site': 'site1',
                                            'lucky': 'blueprint'
                                           }

  s1.config_values[ 'lucky' ] = 'site'
  s1.full_clean()
  s1.save()

  assert _strip_base( getConfig( f1 ) ) == {
                                            '_foundation_class_list': [],
                                            '_foundation_id': 'fdn1',
                                            '_foundation_interface_list': [],
                                            '_foundation_locator': 'fdn1',
                                            '_foundation_state': 'planned',
                                            '_foundation_type': 'Unknown',
                                            '_blueprint': 'fdnb1',
                                            '_site': 'site1',
                                            'lucky': 'site'
                                           }


@pytest.mark.django_db
def test_structure():
  s1 = Site( name='site1', description='test site 1' )
  s1.full_clean()
  s1.save()

  fb1 = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb1.foundation_type_list = [ 'Unknown' ]
  fb1.full_clean()
  fb1.save()

  f1 = Foundation( site=s1, locator='fdn1', blueprint=fb1 )
  f1.full_clean()
  f1.save()

  sb1 = StructureBluePrint( name='strb1', description='Structure BluePrint 1' )
  sb1.full_clean()
  sb1.save()
  sb1.foundation_blueprint_list.add( fb1 )

  str1 = Structure( foundation=f1, site=s1, hostname='struct1', blueprint=sb1 )
  str1.full_clean()
  str1.save()

  now = datetime.now( timezone.utc )
  tmp = getConfig( str1 )
  assert now - tmp[ '__last_modified' ] < timedelta( seconds=5 )
  assert now - tmp[ '__timestamp' ] < timedelta( seconds=5 )

  del tmp[ '__last_modified' ]
  del tmp[ '__timestamp' ]
  del tmp[ '_structure_config_uuid' ]

  assert tmp == {
                  '__contractor_host': 'http://contractor/',
                  '__pxe_location': 'http://static/pxe/',
                  '__pxe_template_location': 'http://contractor/config/pxe_template/',
                  '_foundation_class_list': [],
                  '_foundation_id': 'fdn1',
                  '_foundation_interface_list': [],
                  '_foundation_locator': 'fdn1',
                  '_foundation_state': 'planned',
                  '_foundation_type': 'Unknown',
                  '_provisioning_interface': None,
                  '_provisioning_interface_mac': None,
                  '_structure_id': 7,
                  '_structure_state': 'planned',
                  '_fqdn': 'struct1',
                  '_hostname': 'struct1',
                  '_interface_map': {},
                  '_blueprint': 'strb1',
                  '_site': 'site1'
                }

  assert _strip_base( getConfig( str1 ) ) == {
                                              '_foundation_class_list': [],
                                              '_foundation_id': 'fdn1',
                                              '_foundation_interface_list': [],
                                              '_foundation_locator': 'fdn1',
                                              '_foundation_state': 'planned',
                                              '_foundation_type': 'Unknown',
                                              '_provisioning_interface': None,
                                              '_provisioning_interface_mac': None,
                                              '_structure_id': 7,
                                              '_structure_state': 'planned',
                                              '_fqdn': 'struct1',
                                              '_hostname': 'struct1',
                                              '_interface_map': {},
                                              '_blueprint': 'strb1',
                                              '_site': 'site1'
                                             }

  fb1.config_values[ 'bob' ] = 'foundation blueprint'
  fb1.full_clean()
  fb1.save()

  assert _strip_base( getConfig( str1 ) ) == {
                                              '_foundation_class_list': [],
                                              '_foundation_id': 'fdn1',
                                              '_foundation_interface_list': [],
                                              '_foundation_locator': 'fdn1',
                                              '_foundation_state': 'planned',
                                              '_foundation_type': 'Unknown',
                                              '_provisioning_interface': None,
                                              '_provisioning_interface_mac': None,
                                              '_structure_id': 7,
                                              '_structure_state': 'planned',
                                              '_fqdn': 'struct1',
                                              '_hostname': 'struct1',
                                              '_interface_map': {},
                                              '_blueprint': 'strb1',
                                              '_site': 'site1'
                                             }

  sb1.config_values[ 'bob' ] = 'structure blueprint'
  sb1.full_clean()
  sb1.save()

  assert _strip_base( getConfig( str1 ) ) == {
                                             '_foundation_class_list': [],
                                             '_foundation_id': 'fdn1',
                                             '_foundation_interface_list': [],
                                             '_foundation_locator': 'fdn1',
                                             '_foundation_state': 'planned',
                                             '_foundation_type': 'Unknown',
                                             '_provisioning_interface': None,
                                             '_provisioning_interface_mac': None,
                                             '_structure_id': 7,
                                             '_structure_state': 'planned',
                                             '_fqdn': 'struct1',
                                             '_hostname': 'struct1',
                                             '_interface_map': {},
                                             '_blueprint': 'strb1',
                                             '_site': 'site1',
                                             'bob': 'structure blueprint'
                                            }

  str1.config_values[ 'bob' ] = 'structure'
  str1.full_clean()
  str1.save()

  assert _strip_base( getConfig( str1 ) ) == {
                                             '_foundation_class_list': [],
                                             '_foundation_id': 'fdn1',
                                             '_foundation_interface_list': [],
                                             '_foundation_locator': 'fdn1',
                                             '_foundation_state': 'planned',
                                             '_foundation_type': 'Unknown',
                                             '_provisioning_interface': None,
                                             '_provisioning_interface_mac': None,
                                             '_structure_id': 7,
                                             '_structure_state': 'planned',
                                             '_fqdn': 'struct1',
                                             '_hostname': 'struct1',
                                             '_interface_map': {},
                                             '_blueprint': 'strb1',
                                             '_site': 'site1',
                                             'bob': 'structure'
                                            }
