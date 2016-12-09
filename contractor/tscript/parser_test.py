import pytest
from datetime import timedelta

from contractor.tscript.parser import parse, lint, ParseError


def test_begin():
  node = parse( '' )
  assert node == ( 'S', { '_children': [] } )
  
  node = parse( ' ' )
  assert node == ( 'S', { '_children': [] } )
  
  node = parse( '\n' )
  assert node == ( 'S', { '_children': [] } )
  
  node = parse( ' \n' )
  assert node == ( 'S', { '_children': [] } )
  
  node = parse( '\n\n' )
  assert node == ( 'S', { '_children': [] } )

  node = parse( '10' )
  assert node == ( 'S', { '_children': [ ( 'C', 10 ) ] } )

  node = parse( '10\n42' )
  assert node == ( 'S', { '_children': [ ( 'C', 10 ), ( 'C', 42 ) ] } )

  node = parse( '10\n  42  \n21' )
  assert node == ( 'S', { '_children': [ ( 'C', 10 ), ( 'C', 42 ), ( 'C', 21 ) ] } )


  node = parse( 'begin()end' )
  assert node == ( 'S', { '_children':
                   [
                     ( 'S', { '_children': [] } )
                   ] } )

  node = parse( 'begin()\nend' )
  assert node == ( 'S', { '_children':
                   [
                     ( 'S', { '_children': [] } )
                   ] } )

  node = parse( 'begin( )\nend' )
  assert node == ( 'S', { '_children':
                   [
                     ( 'S', { '_children': [] } )
                   ] } )

  with pytest.raises( ParseError ) as e:
    node = parse( 'begin()' )
  
  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'begin()' ) == 'Incomplete Parsing on line: 1 column: 1'
  assert lint( 'begin()end' ) == None
  assert lint( '' ) == None

  node = parse( 'begin()\n10\nend' )
  assert node == ( 'S', { '_children':
                   [
                     ( 'S', { '_children': [ ( 'C', 10 ) ] } )
                   ] } )


  node = parse( 'begin()\n10\nbegin()end\nend' )
  assert node == ( 'S', { '_children':
                   [
                     ( 'S', { '_children': [ ( 'C', 10 ), ( 'S', { '_children': [] } ) ] } )
                   ] } )


  node = parse( 'begin()\n10\nbegin()\n42\nend\nend' )
  assert node == ( 'S', { '_children':
                   [
                     ( 'S', { '_children': [ ( 'C', 10 ), ( 'S', { '_children': [ ( 'C', 42 ) ] } ) ] } )
                   ] } )

def test_constants():
  node = parse( '10' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 10 )
                 ] } )

  node = parse( '100' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 100 )
                 ] } )

  node = parse( '100000' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 100000 )
                 ] } )
 
  node = parse( '+120' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 120 )
                 ] } )

  node = parse( '-43' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', -43 )
                 ] } )

  node = parse( '10.0' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 10.0 )
                 ] } )
                 
  node = parse( '+120.3' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 120.3 )
                 ] } )

  node = parse( '-43.1' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', -43.1 )
                 ] } )


  node = parse( '0.1' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 0.1 )
                 ] } )
                 
  node = parse( '+0.12' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', .12 )
                 ] } )

  node = parse( '-0.43' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', -.43 )
                 ] } )

  node = parse( 'true' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', True )
                 ] } )

  node = parse( 'True' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', True )
                 ] } )

  node = parse( 'false' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', False )
                 ] } )

  node = parse( 'False' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', False )
                 ] } )

  node = parse( '0:12' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', timedelta( minutes=0, seconds=12 ) )
                 ] } )

  node = parse( '8:22' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', timedelta( minutes=8, seconds=22 ) )
                 ] } )

  node = parse( '2:5:43' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', timedelta( hours=2, minutes=5, seconds=43 ) )
                 ] } )

  node = parse( '9:21:10:01' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', timedelta( days=9, hours=21, minutes=10, seconds=1 ) )
                 ] } )

  node = parse( '"hello"' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 'hello' )
                 ] } )
   
  node = parse( '"isn\'t"' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 'isn\'t' )
                 ] } ) 

  node = parse( "'He said \"hi\"'" )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 'He said "hi"' )
                 ] } ) 

  node = parse( "'nice'" )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 'nice' )
                 ] } )      
  
  node = parse( 'none' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', None )
                 ] } )                       
  
  node = parse( 'None' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', None )
                 ] } )                       


def test_arrays():
  node = parse( '[]' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'Y', [] )
                 ] } )                       

  node = parse( '[ ]' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'Y', [] )
                 ] } )                       

  node = parse( '[1]' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'Y', [ ( 'C', 1 ) ] )
                 ] } )                       


  node = parse( '[ 1 ]' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'Y', [ ( 'C', 1 ) ] )
                 ] } )                       

  node = parse( '[ 1, 2 ]' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'Y', [ ( 'C', 1 ), ( 'C', 2 ) ] )
                 ] } )                       

  node = parse( '[1,2]' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'Y', [ ( 'C', 1 ), ( 'C', 2 ) ] )
                 ] } )                       


  node = parse( '[ 1, 2, "asdf", myval, callme() ]' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'Y', [ ( 'C', 1 ), ( 'C', 2 ), ( 'C', "asdf" ), ( 'V', 'myval' ), ( 'F', { 'name': 'callme', 'paramaters': {} } ) ] )
                 ] } ) 

def test_variables():
  node = parse( 'myval' )
  assert node == ( 'S', { '_children':
               [
                 ( 'V', 'myval' )
               ] } )                  

  node = parse( 'myobj.somthing' )
  assert node == ( 'S', { '_children':
               [
                 ( 'V', 'myobj.somthing' )
               ] } )     


def test_arrayitem():
  node = parse( 'myval[0]' )
  assert node == ( 'S', { '_children':
               [
                 ( 'R', { 'name': 'myval', 'index': ( 'C', 0 ) } )
               ] } )
               
  node = parse( 'myval[ 10 ]' )
  assert node == ( 'S', { '_children':
               [
                 ( 'R', { 'name': 'myval', 'index': ( 'C', 10 ) } )
               ] } )        

  node = parse( 'myval.asdf[ 10 ]' )
  assert node == ( 'S', { '_children':
               [
                 ( 'R', { 'name': 'myval.asdf', 'index': ( 'C', 10 ) } )
               ] } )   

            
def test_infix():
  node = parse( '( 1 + 2 )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } )
               ] } )   

  node = parse( '(1 + 2)' )
  assert node == ( 'S', { '_children':
               [
                 ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } )
               ] } )   


  #node = parse( '( 1+2 )' )
  #assert node == ( 'S', { '_children':
  #             [
  #               ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } )
  #             ] } )   

  #node = parse( '(1+2)' )
  #assert node == ( 'S', { '_children':
  #             [
  #               ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } )
  #             ] } ) 

  node = parse( '(    1   +   2   )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'X', { 'left': ( 'C', 1 ), 'operator': '+', 'right': ( 'C', 2 ) } )
               ] } )   
  
  node = parse( '( ( 1 * 2 ) + 3 )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'X', { 'left': ( 'X', { 'left': ( 'C', 1 ), 'operator': '*', 'right': ( 'C', 2 ) } ), 'operator': '+', 'right': ( 'C', 3 ) } )
               ] } )  

  node = parse( '( 1 * ( 2 + 3 ) )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'X', { 'left': ( 'C', 1 ), 'operator': '*', 'right': ( 'X', { 'left': ( 'C', 2 ), 'operator': '+', 'right': ( 'C', 3 ) } ) } )
               ] } )  


def test_block_paramaters():
  node = parse( 'begin( )\nend' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'S', { '_children': [] } )
                 ] } )
                 
  node = parse( 'begin( )end' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'S', { '_children': [] } )
                 ] } )
                 
  node = parse( 'begin( description="test" )\nend' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'S', { '_children': [], 'description': 'test' } )
                 ] } )
                 
  node = parse( 'begin( description="" )\nend' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'S', { '_children': [], 'description': '' } )
                 ] } )

  node = parse( 'begin( description="test" )end' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'S', { '_children': [], 'description': 'test' } )
                 ] } )

  node = parse( 'begin( description="test", expected_time=12:34 )end' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'S', { '_children': [], 'description': 'test', 'expected_time': timedelta( minutes=12, seconds=34 ) } )
                 ] } )

  node = parse( 'begin( description="test", expected_time=12:34, max_time=1:00:00 )end' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'S', { '_children': [], 'description': 'test', 'expected_time': timedelta( minutes=12, seconds=34 ), 'max_time': timedelta( hours=1 ) } )
                 ] } )


def test_comment():
  node = parse( '#stuff' )
  assert node == ( 'S', { '_children': [] } )
  
  node = parse( '\n#stuff' )
  assert node == ( 'S', { '_children': [] } )
  
  node = parse( '#stuff\n' )
  assert node == ( 'S', { '_children': [] } )
  
  node = parse( '#stuff\n#other#stuff' )
  assert node == ( 'S', { '_children': [] } )

  node = parse( '3 #stuff' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 3 )
                 ] } ) 

  node = parse( '3#stuff' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', 3 )
                 ] } ) 


def test_jumppoint():
  node = parse( ':here' )
  assert node == ( 'S', { '_children':
               [
                 ( 'J', 'here' )
               ] } ) 


def test_while():
  with pytest.raises( ParseError ) as e:
    node = parse( 'while True 10' )
  
  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'while True 10' ) == 'Incomplete Parsing on line: 1 column: 1' 
  
  node = parse( 'while true do 10' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) } )
                 ] } )   

  node = parse( 'while true do \n 10' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) } )
                 ] } )  

  node = parse( 'while true do \n\n 10' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) } )
                 ] } )  


  node = parse( 'while myval do 10' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'V', 'myval' ), 'expression': ( 'C', 10 ) } )
                 ] } )   

  node = parse( 'while ( True == myval ) do 10' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': 
                               ( 'X', { 'left': ( 'C', True ), 'operator': '==', 'right': ( 'V', 'myval' ) } ),
                            'expression': ( 'C', 10 )
                          } )
                 ] } ) 

  node = parse( 'while myval do\nbegin()end' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'V', 'myval' ), 'expression': ( 'S', { '_children':
                     [
                     ]
                   } ) } )
                 ] } ) 

  node = parse( 'while myval do\nbegin()\n10\nend' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'V', 'myval' ), 'expression': ( 'S', { '_children':
                     [
                       ( 'C', 10 )
                     ]
                   } ) } )
                 ] } ) 
      
  node = parse( 'while myval do\nbegin(thep=5)\n10\nend' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'V', 'myval' ), 'expression': ( 'S', { 'thep': 5, '_children':
                     [
                       ( 'C', 10 )
                     ]
                   } ) } )
                 ] } ) 
      
  node = parse( 'continue' )
  assert node == ( 'S', { '_children': [ ( 'O', 'continue' ) ] } )
  
  node = parse( 'break' )
  assert node == ( 'S', { '_children': [ ( 'O', 'break' ) ] } )

  node = parse( 'while myval do\nbegin()\n10\ncontinue\nend' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'W', { 'condition': ( 'V', 'myval' ), 'expression': ( 'S', { '_children':
                     [
                       ( 'C', 10 ),
                       ( 'O',  'continue' )
                     ]
                   } ) } )
                 ] } ) 
      
      
def test_ifelse():   
  with pytest.raises( ParseError ) as e:
    node = parse( 'if True 10' )
  
  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'if True 10' ) == 'Incomplete Parsing on line: 1 column: 1' 
   
  node = parse( 'if True then 10' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'I', [ 
                            { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) }
                          ] )
                 ] } )   

  node = parse( 'if True then 10 else 42' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'I', [ 
                            { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                            { 'condition': None, 'expression': ( 'C', 42 ) }
                          ] )
                 ] } )             

  node = parse( 'if True then\n10\nelse\n42' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'I', [ 
                            { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                            { 'condition': None, 'expression': ( 'C', 42 ) }
                          ] )
                 ] } )  

  with pytest.raises( ParseError ) as e:
    node = parse( 'if True then 10 elif False 200 else 42' )
  
  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'if True then 10 elif False 200 else 42' ) == 'Incomplete Parsing on line: 1 column: 1' 

  node = parse( 'if True then 10 elif False then 200 else 42' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'I', [ 
                            { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                            { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                            { 'condition': None, 'expression': ( 'C', 42 ) }
                          ] )
                 ] } )  

  node = parse( 'if True then\n10\nelif False then\n200\nelse\n42' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'I', [ 
                            { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                            { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                            { 'condition': None, 'expression': ( 'C', 42 ) }
                          ] )
                 ] } )

  node = parse( 'if True then 10 elif ( asdf == "a" ) then 100 elif False then 200 else 42' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'I', [ 
                            { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                            { 'condition': ( 'X', { 'left': ( 'V', 'asdf' ), 'operator': '==', 'right': ( 'C', 'a' ) } ), 'expression': ( 'C', 100 ) },
                            { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                            { 'condition': None, 'expression': ( 'C', 42 ) }
                          ] )
                 ] } ) 
                
  node = parse( 'if True then\n10\nelif ( asdf == "a" ) then\n100\nelif False then\n200\nelse\n42' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'I', [ 
                            { 'condition': ( 'C', True ), 'expression': ( 'C', 10 ) },
                            { 'condition': ( 'X', { 'left': ( 'V', 'asdf' ), 'operator': '==', 'right': ( 'C', 'a' ) } ), 'expression': ( 'C', 100 ) },
                            { 'condition': ( 'C', False ), 'expression': ( 'C', 200 ) },
                            { 'condition': None, 'expression': ( 'C', 42 ) }
                          ] )
                 ] } ) 

            
def test_variable():
  node = parse( 'myval' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'V', 'myval' )
                 ] } )
                 
  node = parse( 'myval.subval' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'V', 'myval.subval' )
                 ] } )

  node = parse( 'myval.subval.andmore' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'V', 'myval.subval.andmore' )
                 ] } )


def test_not():
  node = parse( 'False' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'C', False )
                 ] } )
                 
  node = parse( 'not False' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'N', ( 'C', False ) )
                 ] } )
 
  node = parse( 'Not True' )
  assert node == ( 'S', { '_children':
                 [
                   ( 'N', ( 'C', True ) )
                 ] } )
                 
def test_function():
  node = parse( 'hello()' )
  assert node == ( 'S', { '_children':
               [
                 ( 'F', { 'name': 'hello', 'paramaters': {} } )
               ] } )

  node = parse( 'hello( )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'F', { 'name': 'hello', 'paramaters': {} } )
               ] } )

  node = parse( 'more.hello()' )
  assert node == ( 'S', { '_children':
               [
                 ( 'F', { 'name': 'more.hello', 'paramaters': {} } )
               ] } )

  with pytest.raises( ParseError ) as e:
    node = parse( 'hello( 10 )' )
  
  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'

  assert lint( 'hello( 10 )' ) == 'Incomplete Parsing on line: 1 column: 1' 
  
  node = parse( 'hello( asdf = 10 )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'F', { 'name': 'hello', 'paramaters': { 'asdf': ( 'C', 10 ) } } )
               ] } )

  node = parse( 'hello( asdf = "" )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'F', { 'name': 'hello', 'paramaters': { 'asdf': ( 'C', '' ) } } )
               ] } )

  node = parse( 'hello(asdf=10)' )
  assert node == ( 'S', { '_children':
               [
                 ( 'F', { 'name': 'hello', 'paramaters': { 'asdf': ( 'C', 10 ) } } )
               ] } )

               
  node = parse( 'hello( asdf = 10, zxcv="hi", qwerty=123 )' )
  assert node == ( 'S', { '_children':
               [
                 ( 'F', { 'name': 'hello', 'paramaters': { 'asdf': ( 'C', 10 ), 'zxcv': ( 'C', 'hi' ), 'qwerty': ( 'C', 123 ) } } )
               ] } )
               
def test_assignment():
  with pytest.raises( ParseError ) as e:
    node = parse( 'asdf=' )
  
  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'
 
  assert lint( 'asdf=' ) == 'Incomplete Parsing on line: 1 column: 1' 

  with pytest.raises( ParseError ) as e:
    node = parse( 'asdf =' )
  
  assert str( e.value ) == 'ParseError, line: 1, column: 1, "Incomplete Parse"'
  
  assert lint( 'asdf =' ) == 'Incomplete Parsing on line: 1 column: 1' 

  node = parse( 'asdf=5' )
  assert node == ( 'S', { '_children':
              [
                ( 'A', { 'target': ( 'V', 'asdf' ), 'value': ( 'C', 5 ) } )
              ] } )
             
  node = parse( 'asdf = 5' )
  assert node == ( 'S', { '_children':
              [
                ( 'A', { 'target': ( 'V', 'asdf' ), 'value': ( 'C', 5 ) } )
              ] } )

  node = parse( 'asdf.fdsa = 5' )
  assert node == ( 'S', { '_children':
              [
                ( 'A', { 'target': ( 'V', 'asdf.fdsa' ), 'value': ( 'C', 5 ) } )
              ] } )
             
  node = parse( 'asdf = myfunc()' )
  assert node == ( 'S', { '_children':
              [
                ( 'A', { 'target': ( 'V', 'asdf' ), 'value': ( 'F', { 'name': 'myfunc', 'paramaters': {} } ) } )
              ] } )
             
  node = parse( 'asdf = myval' )
  assert node == ( 'S', { '_children':
              [
                ( 'A', { 'target': ( 'V', 'asdf' ), 'value': ( 'V', 'myval' ) } )
              ] } )
              
  node = parse( 'asdf[3] = myval' )
  assert node == ( 'S', { '_children':
              [
                ( 'A', { 'target': ( 'R', { 'name': 'asdf', 'index': ( 'C', 3 ) } ), 'value': ( 'V', 'myval' ) } )
              ] } )
