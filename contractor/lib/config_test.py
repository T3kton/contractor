import pytest

from contractor.Site.models import Site
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

  # values = { 'a': 1, 'd': '{{a}}', 'e': '"{{a}}"' }
  # assert { 'a': 'c', 'd': 1, 'e': '1' } == mergeValues( values )
  # assert { 'a': 'c', 'd': '{{a}}', 'e': '"{{a}}"' } == values

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


def _strip_dates( value ):
  del value[ '__last_modified' ]
  del value[ '__timestamp' ]
  return value


@pytest.mark.django_db
def test_site():
  s1 = Site( name='site1', description='test site 1' )
  s1.config_values = {}
  s1.full_clean()
  s1.save()

  assert _strip_dates( getConfig( s1 ) ) == {
                                               '__contractor_host': 'http://contractor/',
                                               '__pxe_location': 'http://static/pxe/',
                                               '__pxe_template_location': 'http://contractor/config/pxe_template/',
                                               'site': 'site1'
                                            }

  s2 = Site( name='site2', description='test site 2', parent=s1 )
  s2.config_values = { 'myval': 'this is a test', 'stuff': 'this is only a test' }
  s2.full_clean()
  s2.save()

  assert _strip_dates( getConfig( s2 ) ) == {
                                               '__contractor_host': 'http://contractor/',
                                               '__pxe_location': 'http://static/pxe/',
                                               '__pxe_template_location': 'http://contractor/config/pxe_template/',
                                               'site': 'site2',
                                               'myval': 'this is a test',
                                               'stuff': 'this is only a test'
                                            }

  s1.config_values = { 'under': 'or over' }
  s1.full_clean()
  s1.save()

  assert _strip_dates( getConfig( s2 ) ) == {
                                               '__contractor_host': 'http://contractor/',
                                               '__pxe_location': 'http://static/pxe/',
                                               '__pxe_template_location': 'http://contractor/config/pxe_template/',
                                               'site': 'site2',
                                               'myval': 'this is a test',
                                               'stuff': 'this is only a test',
                                               'under': 'or over'
                                            }

  s2.config_values[ '>under' ] = ' here'
  s2.config_values[ '<under' ] = 'going '
  s2.full_clean()
  s2.save()

  assert _strip_dates( getConfig( s2 ) ) == {
                                               '__contractor_host': 'http://contractor/',
                                               '__pxe_location': 'http://static/pxe/',
                                               '__pxe_template_location': 'http://contractor/config/pxe_template/',
                                               'site': 'site2',
                                               'myval': 'this is a test',
                                               'stuff': 'this is only a test',
                                               'under': 'going or over here'
                                            }
