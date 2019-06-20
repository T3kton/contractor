import pytest

from contractor.Foreman.runner_plugins.building import SetConfig
from contractor.tscript.runner import ParamaterError


class fakeStructure():
  def __init__( self, config_map ):
    self.config_values = config_map

  def full_clean( self ):
    pass

  def save( self, update_fields ):
    pass


def test_setconfig():
  s = fakeStructure( { 'a': 2, 'b': 10 } )
  sc = SetConfig( s )
  sc( 'a', 4 )
  assert s.config_values == { 'a': 4, 'b': 10 }

  s = fakeStructure( { 'a': 2 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'b', 4 )
  assert s.config_values == { 'a': 2 }

  s = fakeStructure( { 'a': 2, 'b': 10 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'a.b', 4 )
  assert s.config_values == { 'a': 2, 'b': 10 }

  s = fakeStructure( { 'a': 2, 'b': 10 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'a.b.c', 4 )
  assert s.config_values == { 'a': 2, 'b': 10 }

  s = fakeStructure( { 'a': { 'a': 3 }, 'b': 10 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'a.b', 4 )
  assert s.config_values == { 'a': { 'a': 3 }, 'b': 10 }

  s = fakeStructure( { 'a': { 'b': 3 }, 'b': 10 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'a.a.b', 4 )
  assert s.config_values == { 'a': { 'b': 3 }, 'b': 10 }

  s = fakeStructure( { 'a': { 'b': 3 }, 'b': 10 } )
  sc = SetConfig( s )
  sc( 'a.b', 4 )
  assert s.config_values == { 'a': { 'b': 4 }, 'b': 10 }

  s = fakeStructure( { 'a': [], 'b': 10 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'a.b', 4 )
  assert s.config_values == { 'a': [], 'b': 10 }

  s = fakeStructure( { 'a': [], 'b': 10 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'a.1', 4 )
  assert s.config_values == { 'a': [], 'b': 10 }

  s = fakeStructure( { 'a': [ 1, 2, 3, 4 ], 'b': 10 } )
  sc = SetConfig( s )
  sc( 'a.1', 4 )
  assert s.config_values == { 'a': [ 1, 4, 3, 4 ], 'b': 10 }

  s = fakeStructure( { 'a': [ 1, { 'a': 11, 'c': 12 }, 3, 4 ], 'b': 10 } )
  sc = SetConfig( s )
  sc( 'a.1.c', 4 )
  assert s.config_values == { 'a': [ 1, { 'a': 11, 'c': 4 }, 3, 4 ], 'b': 10 }

  s = fakeStructure( { 'a|d': 2, 'b': 10 } )
  sc = SetConfig( s )
  with pytest.raises( ParamaterError ):
    sc( 'a|d', 4 )
  assert s.config_values == { 'a|d': 2, 'b': 10 }

  s = fakeStructure( { 'a': { 'a|d': 2 }, 'b': 10 } )
  sc = SetConfig( s )
  sc( 'a.a|d', 4 )
  assert s.config_values == { 'a': { 'a|d': 4 }, 'b': 10 }
