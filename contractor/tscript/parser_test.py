import pytest
from datetime import timedelta

from contractor.tscript.parser import parse, lint, ParserError, Parser


def test_gramer_parses():
  Parser()


def test_begin():
  node = parse( '' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( ' ' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( '\n' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( ' \n' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( '\n\n' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( '10' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( ' 10' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( '10\n' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( '   10\n' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( '10\n42' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 1 ), ( 'L', ( 'C', 42 ), 2 ) ], 'description': 'Overall Script' } )

  node = parse( '10\n  42  \n21' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 1 ), ( 'L', ( 'C', 42 ), 2 ), ( 'L', ( 'C', 21 ), 3 ) ], 'description': 'Overall Script' } )

  node = parse( '   10\n  42  \n21  ' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 1 ), ( 'L', ( 'C', 42 ), 2 ), ( 'L', ( 'C', 21 ), 3 ) ], 'description': 'Overall Script' } )

  node = parse( 'begin()end' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [] } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'begin()\nend' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [] } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'begin( )\nend' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [] } ), 1 )
                   ], 'description': 'Overall Script' } )

  with pytest.raises( ParserError ) as e:
    parse( 'begin()' )

  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'begin()' ) == 'Incomplete Parsing on line: 1 column: 1'
  assert lint( 'begin()end' ) is None
  assert lint( '' ) is None

  node = parse( 'begin()\n10\nend' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 2 ) ] } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'begin()\n10\nbegin()end\nend' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 2 ), ( 'L', ( 'S', { '_children': [] } ), 3 ) ] } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'begin()\n10\nbegin()\n42\nend\nend' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 2 ), ( 'L', ( 'S', { '_children': [ ( 'L', ( 'C', 42 ), 4 ) ] } ), 3 ) ] } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'begin()\n  10\nend' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 2 ) ] } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'begin()\n  10\n  begin()\n    42\n  end\nend' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'S', { '_children': [ ( 'L', ( 'C', 10 ), 2 ), ( 'L', ( 'S', { '_children': [ ( 'L', ( 'C', 42 ), 4 ) ] } ), 3 ) ] } ), 1 )
                   ], 'description': 'Overall Script' } )


def test_constants():
  node = parse( '10' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 10 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '100' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 100 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '100000' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 100000 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '+120' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 120 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '-43' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', -43 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '10.0' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 10.0 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '+120.3' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 120.3 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '-43.1' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', -43.1 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '0.1' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 0.1 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '+0.12' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', .12 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '-0.43' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', -.43 ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'true' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', True ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'True' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', True ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'false' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', False ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'False' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', False ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '0:12' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', timedelta( minutes=0, seconds=12 ) ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '8:22' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', timedelta( minutes=8, seconds=22 ) ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '2:5:43' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', timedelta( hours=2, minutes=5, seconds=43 ) ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '9:21:10:01' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', timedelta( days=9, hours=21, minutes=10, seconds=1 ) ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '"hello"' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 'hello' ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '"isn\'t"' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 'isn\'t' ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( "'He said \"hi\"'" )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 'He said "hi"' ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( "'nice'" )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 'nice' ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'none' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', None ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( 'None' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', None ), 1 )
                   ], 'description': 'Overall Script' } )


def test_arrays():
  node = parse( '[]' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'Y', [] ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '[ ]' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'Y', [] ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '[1]' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'Y', [ ( 'C', 1 ) ] ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '[ 1 ]' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'Y', [ ( 'C', 1 ) ] ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '[ 1, 2 ]' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'Y', [ ( 'C', 1 ), ( 'C', 2 ) ] ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '[1,2]' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'Y', [ ( 'C', 1 ), ( 'C', 2 ) ] ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '[ 1, 2, "asdf", myval, callme() ]' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'Y', [ ( 'C', 1 ), ( 'C', 2 ), ( 'C', 'asdf' ), ( 'V', { 'module': None, 'name': 'myval' } ), ( 'F', { 'module': None, 'name': 'callme', 'paramaters': {} } ) ] ), 1 )
                   ], 'description': 'Overall Script' } )


def test_maps():
  node = parse( '{}' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'M', {} ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '{ }' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'M', {} ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '{asdf=10}' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'M', { 'asdf': ( 'C', 10 ) } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '{ asdf = 10 }'  )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'M', { 'asdf': ( 'C', 10 ) } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '{ asdf = "10" }'  )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'M', { 'asdf': ( 'C', '10') } ), 1 )
                   ], 'description': 'Overall Script' } )

  node = parse( '{ asdf = "10", qwerty = 10 }'  )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'M', { 'asdf': ( 'C', '10' ), 'qwerty': ( 'C', 10 ) } ), 1 )
                   ], 'description': 'Overall Script' } )

  with pytest.raises( ParserError ):
    parse( '{ asdf: "10" }'  )

  with pytest.raises( ParserError ):
    parse( '{ "10" }'  )


def test_variables():
  node = parse( 'myval' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': None, 'name': 'myval' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'myobj.somthing' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': 'myobj', 'name': 'somthing' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'myobj.somthing' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': 'myobj', 'name': 'somthing' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'good2go' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': None, 'name': 'good2go' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'good2go.go4win' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': 'good2go', 'name': 'go4win' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'var2' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': None, 'name': 'var2' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'mod1.var2' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': 'mod1', 'name': 'var2' } ), 1 )
                          ], 'description': 'Overall Script' } )

  # all invalid names
  with pytest.raises( ParserError ):
    parse( 'a' )

  with pytest.raises( ParserError ):
    parse( 'a.b' )

  with pytest.raises( ParserError ):
    parse( '2a' )

  with pytest.raises( ParserError ):
    parse( 'adsf.2a' )

  # prefixed reserved
  with pytest.raises( ParserError ):
    parse( 'do' )

  node = parse( 'docker' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': None, 'name': 'docker' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'got' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': None, 'name': 'got' } ), 1 )
                          ], 'description': 'Overall Script' } )

  with pytest.raises( ParserError ):
    parse( 'goto' )

  node = parse( 'gotoing' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'V', { 'module': None, 'name': 'gotoing' } ), 1 )
                          ], 'description': 'Overall Script' } )


def test_arrayitem():
  node = parse( 'myval[0]' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'R', { 'module': None, 'name': 'myval', 'index': ( 'C', 0 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'myval[ 10 ]' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'R', { 'module': None, 'name': 'myval', 'index': ( 'C', 10 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'myval.asdf[ 10 ]' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'R', { 'module': 'myval', 'name': 'asdf', 'index': ( 'C', 10 ) } ), 1 )
                          ], 'description': 'Overall Script' } )


def test_infix():
  node = parse( '( 1 + 2 )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( '(1 + 2)' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( '( 1+2 )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( '(1+2)' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( '(    1   +   2   )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( '( ( 1 * 2 ) + 3 )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'X', { 'left': ( 'X', { 'left': ( 'C', 1 ), 'operator': '*', 'right': ( 'C', 2 ) } ), 'operator': '+', 'right': ( 'C', 3 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( '( 1 * ( 2 + 3 ) )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'X', { 'left': ( 'C', 1 ), 'operator': '*', 'right': ( 'X', { 'left': ( 'C', 2 ), 'operator': '+', 'right': ( 'C', 3 ) } ) } ), 1 )
                          ], 'description': 'Overall Script' } )


def test_block_paramaters():
  node = parse( 'begin( )\nend' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'S', { '_children': [] } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'begin( )end' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'S', { '_children': [] } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'begin( description="test" )\nend' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'S', { '_children': [], 'description': 'test' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'begin( description="" )\nend' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'S', { '_children': [], 'description': '' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'begin( description="test" )end' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'S', { '_children': [], 'description': 'test' } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'begin( description="test", expected_time=12:34 )end' )
  assert node == ( 'S', { '_children':
                          [
                                ( 'L', ( 'S', { '_children': [], 'description': 'test', 'expected_time': timedelta( minutes=12, seconds=34 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'begin( description="test", expected_time=12:34, max_time=1:00:00 )end' )
  assert node == ( 'S', { '_children':
                          [
                                ( 'L', ( 'S', { '_children': [], 'description': 'test', 'expected_time': timedelta( minutes=12, seconds=34 ), 'max_time': timedelta( hours=1 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  with pytest.raises( Exception ):
    parse( 'begin( bogus="test", expected_time=12:34 )end' )


def test_comment():
  node = parse( '#stuff' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( '\n#stuff' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( '#stuff\n' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( '#stuff\n#other#stuff' )
  assert node == ( 'S', { '_children': [], 'description': 'Overall Script' } )

  node = parse( '3 #stuff' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 3 ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( '3#stuff' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', 3 ), 1 )
                          ], 'description': 'Overall Script' } )


def test_jumppoint():
  node = parse( ':here' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'J', 'here' ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'goto there' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'G', 'there' ), 1 )
                          ], 'description': 'Overall Script' } )

  with pytest.raises( ParserError ) as e:
    parse( 'begin()\n:there\nend' )

  assert str( e.value ) == 'ParseError, line: 2, column: 0, "Jump points can not be inside begin/end blocks, jump point name: "there""'

  assert lint( 'begin()\n:there\nend' ) == 'Invalid Script "Jump points can not be inside begin/end blocks, jump point name: "there"", line: 2 column: 0'

  with pytest.raises( ParserError ) as e:
    parse( '1\nbegin()\n:other\nend' )

  assert str( e.value ) == 'ParseError, line: 3, column: 0, "Jump points can not be inside begin/end blocks, jump point name: "other""'

  assert lint( '1\nbegin()\n:other\nend' ) == 'Invalid Script "Jump points can not be inside begin/end blocks, jump point name: "other"", line: 3 column: 0'

  with pytest.raises( ParserError ) as e:
    parse( 'begin()\n1\nbegin()\n1\n:stuff\nend\nend' )

  assert str( e.value ) == 'ParseError, line: 5, column: 0, "Jump points can not be inside begin/end blocks, jump point name: "stuff""'

  assert lint( 'begin()\n1\nbegin()\n1\n:stuff\nend\nend' ) == 'Invalid Script "Jump points can not be inside begin/end blocks, jump point name: "stuff"", line: 5 column: 0'


def test_while():
  with pytest.raises( ParserError ) as e:
    parse( 'while True 10' )

  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'while True 10' ) == 'Incomplete Parsing on line: 1 column: 1'

  node = parse( 'while true do 10' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'W', { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while true do \n 10' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'W', { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while true do \n\n 10' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'W', { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while true do \n  \n 10' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'W', { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while myval do 10' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'W', { 'condition': ( 'V', { 'module': None, 'name': 'myval' } ), 'expression': ( 'C', 10 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while ( True == myval ) do 10' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'W', { 'condition':
                                               ( 'X', { 'left': ( 'C', True ), 'operator': '==', 'right': ( 'V', { 'module': None, 'name': 'myval' } ) } ),
                                        'expression': ( 'C', 10 )
                                               } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while myval do\nbegin()end' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'W', { 'condition': ( 'V', { 'module': None, 'name': 'myval' } ), 'expression': ( 'S', { '_children':
                                 [
                                 ]
                               } ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while myval do\nbegin()\n10\nend' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'W', { 'condition': ( 'V', { 'module': None, 'name': 'myval' } ), 'expression': ( 'S', { '_children':
                                 [
                                      ( 'L', ( 'C', 10 ), 3 )
                                 ]
                               } ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'while myval do\nbegin(description="5")\n10\nend' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'W', { 'condition': ( 'V', { 'module': None, 'name': 'myval' } ), 'expression': ( 'S', { 'description': '5', '_children':
                                 [
                                      ( 'L', ( 'C', 10 ), 3 )
                                 ]
                               } ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'continue' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'O', 'continue' ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'break' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'O', 'break' ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'while myval do\nbegin()\n10\ncontinue\nend' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'W', { 'condition': ( 'V', { 'module': None, 'name': 'myval' } ), 'expression': ( 'S', { '_children':
                                 [
                                     ( 'L', ( 'C', 10 ), 3 ),
                                     ( 'L', ( 'O', 'continue' ), 4 )
                                 ]
                               } ) } ), 1 )
                          ], 'description': 'Overall Script' } )


def test_ifelse():
  with pytest.raises( ParserError ) as e:
    parse( 'if True 10' )

  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'if True 10' ) == 'Incomplete Parsing on line: 1 column: 1'

  node = parse( 'if True then 10' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then 10 else 42' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                                        { 'condition': None, 'expression': ( 'C', 42 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then\n10\nelse\n42' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                                        { 'condition': None, 'expression': ( 'C', 42 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  with pytest.raises( ParserError ) as e:
    parse( 'if True then 10 elif False 200 else 42' )

  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'if True then 10 elif False 200 else 42' ) == 'Incomplete Parsing on line: 1 column: 1'

  node = parse( 'if True then 10 elif False then 200 else 42' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                                        { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                                        { 'condition': None, 'expression': ( 'C', 42 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then\n10\nelif False then\n200\nelse\n42' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                                        { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                                        { 'condition': None, 'expression': ( 'C', 42 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then 10 elif ( asdf == "a" ) then 100 elif False then 200 else 42' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                                        { 'condition': ( 'X', { 'left': ( 'V', { 'module': None, 'name': 'asdf' }  ), 'operator': '==', 'right': ( 'C', 'a' ) } ), 'expression': ( 'C', 100 ) },
                                        { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                                        { 'condition': None, 'expression': ( 'C', 42 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then\n10\nelif ( asdf == "a" ) then\n100\nelif False then\n200\nelse\n42' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                                        { 'condition': ( 'X', { 'left': ( 'V', { 'module': None, 'name': 'asdf' } ), 'operator': '==', 'right': ( 'C', 'a' ) } ), 'expression': ( 'C', 100 ) },
                                        { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                                        { 'condition': None, 'expression': ( 'C', 42 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if ( myobj.value >= "my string" ) then\nbegin( description="this" )\n42\nend' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                       { 'condition': ( 'X',
                                                        { 'left': ( 'V', { 'module': 'myobj', 'name': 'value' } ), 'operator': '>=', 'right': ( 'C', "my string" ) } ),
                                        'expression': ( 'S', { 'description': 'this', '_children': [ ( 'L', ( 'C', 42 ), 3 ) ] } ),
                                         } ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if ( myobj.value >= "my string" ) then\nbegin( description="this" )\n42\nend\nelse\nbegin( max_time=1:20 )\n56\nend' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                       {
                                           'condition': ( 'X',
                                                          { 'left': ( 'V', { 'module': 'myobj', 'name': 'value' } ), 'operator': '>=', 'right': ( 'C', "my string" ) } ),
                                           'expression': ( 'S', { 'description': 'this', '_children': [ ( 'L', ( 'C', 42 ), 3 ) ] } ),
                                       },
                                       {
                                           'condition': None,
                                           'expression': ( 'S', { 'max_time': timedelta(seconds=80), '_children': [ ( 'L', ( 'C', 56 ), 7 ) ] } ),
                                       }
                                     ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then\n42\nelse\n56' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 42 ) },
                                        { 'condition': None, 'expression': ( 'C', 56 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then  \n  42  \n  \n  \n  else  \n  56' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 42 ) },
                                        { 'condition': None, 'expression': ( 'C', 56 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then\n42\nelif False then\n32\nelse\n56' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 42 ) },
                                        { 'condition': ( 'C', False ), 'expression': ( 'C', 32 ) },
                                        { 'condition': None, 'expression': ( 'C', 56 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'if True then  \n  42  \n  \n  \n  elif False then\n  32  \n  \n  \n  else  \n  56' )
  assert node == ( 'S', { '_children':
                          [
                               ( 'L', ( 'I', [
                                        { 'condition': ( 'C', True ), 'expression': ( 'C', 42 ) },
                                        { 'condition': ( 'C', False ), 'expression': ( 'C', 32 ) },
                                        { 'condition': None, 'expression': ( 'C', 56 ) }
                                        ] ), 1 )
                          ], 'description': 'Overall Script' } )


def test_not():
  node = parse( 'False' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'C', False ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'not False' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'X', { 'operator': 'not', 'left': ( 'C', False ), 'right': ( 'C', None ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'Not True' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'X', { 'operator': 'not', 'left': ( 'C', True ), 'right': ( 'C', None ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'not adsf' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'X', { 'operator': 'not', 'left': ( 'V', { 'name': 'adsf', 'module': None } ), 'right': ( 'C', None ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'not asdf.wert' )
  assert node == ( 'S', { '_children':
                   [
                       ( 'L', ( 'X', { 'operator': 'not', 'left': ( 'V', { 'name': 'wert', 'module': 'asdf' } ), 'right': ( 'C', None ) } ), 1 )
                          ], 'description': 'Overall Script' } )


def test_function():
  node = parse( 'hello()' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'F', { 'module': None, 'name': 'hello', 'paramaters': {} } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'hello( )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'F', { 'module': None, 'name': 'hello', 'paramaters': {} } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'more.hello()' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'F', { 'module': 'more', 'name': 'hello', 'paramaters': {} } ), 1 )
                          ], 'description': 'Overall Script' } )

  with pytest.raises( ParserError ) as e:
    parse( 'hello( 10 )' )

  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'hello( 10 )' ) == 'Incomplete Parsing on line: 1 column: 1'

  node = parse( 'hello( asdf = 10 )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'F', { 'module': None, 'name': 'hello', 'paramaters': { 'asdf': ( 'C', 10 ) } } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'hello( asdf = "" )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'F', { 'module': None, 'name': 'hello', 'paramaters': { 'asdf': ( 'C', '' ) } } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'hello(asdf=10)' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'F', { 'module': None, 'name': 'hello', 'paramaters': { 'asdf': ( 'C', 10 ) } } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'hello( asdf = 10, zxcv="hi", qwerty=123 )' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'F', { 'module': None, 'name': 'hello', 'paramaters': { 'asdf': ( 'C', 10 ), 'zxcv': ( 'C', 'hi' ), 'qwerty': ( 'C', 123 ) } } ), 1 )
                          ], 'description': 'Overall Script' } )


def test_assignment():
  with pytest.raises( ParserError ) as e:
    parse( 'asdf=' )

  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'asdf=' ) == 'Incomplete Parsing on line: 1 column: 1'

  with pytest.raises( ParserError ) as e:
    parse( 'asdf =' )

  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'asdf =' ) == 'Incomplete Parsing on line: 1 column: 1'

  node = parse( 'asdf=5' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'A', { 'target': ( 'V', { 'module': None, 'name': 'asdf' } ), 'value': ( 'C', 5 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'asdf = 5' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'A', { 'target': ( 'V', { 'module': None, 'name': 'asdf' } ), 'value': ( 'C', 5 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'asdf.fdsa = 5' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'A', { 'target': ( 'V', { 'module': 'asdf', 'name': 'fdsa' } ), 'value': ( 'C', 5 ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'asdf = myfunc()' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'A', { 'target': ( 'V', { 'module': None, 'name': 'asdf' } ), 'value': ( 'F', { 'module': None, 'name': 'myfunc', 'paramaters': {} } ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'asdf = myval' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'A', { 'target': ( 'V', { 'module': None, 'name': 'asdf' } ), 'value': ( 'V', { 'module': None, 'name': 'myval' } ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'asdf = not myval' )
  assert node == ( 'S', { '_children':
                          [
                              ( 'L', ( 'A', { 'target': ( 'V', { 'module': None, 'name': 'asdf' } ), 'value': ( 'X', { 'operator': 'not', 'left': ( 'V', { 'module': None, 'name': 'myval' } ), 'right': ( 'C', None ) } ) } ), 1 )
                          ], 'description': 'Overall Script' } )

  node = parse( 'asdf[3] = myval' )
  assert node == ( 'S', { '_children':
                          [
                                ( 'L', ( 'A', { 'target': ( 'R', { 'module': None, 'name': 'asdf', 'index': ( 'C', 3 ) } ), 'value': ( 'V', { 'module': None, 'name': 'myval' } ) } ), 1 )
                          ], 'description': 'Overall Script' } )


def test_exists():
  node = parse( 'exists( bob )' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'E', ( 'V', { 'module': None, 'name': 'bob' } ) ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'exists( top.bottom )' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'E', ( 'V', { 'module': 'top', 'name': 'bottom' } ) ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'exists(bob2)' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'E', ( 'V', { 'module': None, 'name': 'bob2' } ) ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'exists( bob3)' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'E', ( 'V', { 'module': None, 'name': 'bob3' } ) ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'exists(bob4 )' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'E', ( 'V', { 'module': None, 'name': 'bob4' } ) ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'exists( bob[1] )' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'E', ( 'R', { 'index': ( 'C', 1 ), 'module': None, 'name': 'bob' } ) ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'exists( bob[gh] )' )
  assert node == ( 'S', { '_children': [ ( 'L', ( 'E', ( 'R', { 'index': ( 'V', { 'module': None, 'name': 'gh' } ), 'module': None, 'name': 'bob' } ) ), 1 ) ], 'description': 'Overall Script' } )

  node = parse( 'aa = exists( bob )' )
  assert node == ( 'S', { '_children': [ ( 'L',
                   ( 'A',
                     { 'target': ( 'V', { 'module': None, 'name': 'aa' } ),
                       'value': ( 'E', ( 'V', { 'module': None, 'name': 'bob' } ) )
                       }
                     ),
                  1 ) ], 'description': 'Overall Script' } )

  node = parse( 'if exists( bob ) then 10' )
  assert node == ( 'S', { '_children': [ ( 'L',
                   ( 'I',
                       [ { 'condition': ( 'E', ( 'V', { 'module': None, 'name': 'bob' } ) ),
                           'expression': ( 'C', 10 ) }
                         ] ),
                    1 ) ], 'description': 'Overall Script' } )
