import pytest

from contractor.lib.config import _updateConfig, mergeValues


def test_string():
  config = {}
  _updateConfig( {}, [], config )
  assert config == {}


def test_mergeValues():
  values = { 'a': 'c' }
  assert { 'a': 'c' } == mergeValues( values )
  assert { 'a': 'c' } == values

  values = { 'a': 3 }
  assert { 'a': 3 } == mergeValues( values )
  assert { 'a': 3 } == values

  values = { 'a': 'c', 'd': '{{a}}' }
  assert { 'a': 'c', 'd': 'c' } == mergeValues( values )
  assert { 'a': 'c', 'd': '{{a}}' } == values

  values = { 'a': 'c', 'd': '{{z|default(\'v\')}}' }
  assert { 'a': 'c', 'd': 'v' } == mergeValues( values )
  assert { 'a': 'c', 'd': '{{z|default(\'v\')}}' } == values

  values = { 'a': 'c', 'd': '{{a|default(\'v\')}}' }
  assert { 'a': 'c', 'd': 'c' } == mergeValues( values )
  assert { 'a': 'c', 'd': '{{a|default(\'v\')}}' } == values

  values = { 'a': 'c', 'd': { 'bob': 'sdf', 'sally': '{{a}}' } }
  assert { 'a': 'c', 'd': { 'bob': 'sdf', 'sally': 'c' } } == mergeValues( values )
  assert { 'a': 'c', 'd': { 'bob': 'sdf', 'sally': '{{a}}' } } == values
