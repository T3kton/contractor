import pytest
import pickle
import time

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner, ExecutionError, UnrecoverableError, ParamaterError, NotDefinedError, Timeout, Pause

# TODO: test the assignment deepcopy, ie: a = {}, b = a  make sure changes to b are not reflected in a


class testExternalObject( object ):
  TSCRIPT_NAME = 'test_obj'

  def __init__( self, dataRW, dataWO, dataRO ):
    super().__init__()
    self.dataRW = dataRW
    self.dataWO = dataWO
    self.dataRO = dataRO

  def getValues( self ):
    return {
             'dataRW': ( lambda: self.dataRW, lambda val: setattr( self, 'dataRW', val ) ),
             'dataWO': ( None, lambda val: setattr( self, 'dataWO', val ) ),
             'dataRO': ( lambda: self.dataRO, None )
            }

  def getFunctions( self ):  # TODO: test exteral object functions, also module override
    result = {}

    return result

  def __reduce__( self ):
    return ( self.__class__, ( self.dataRW, self.dataWO, self.dataRO ) )


def test_begin():
  runner = Runner( parse( '' ) )
  assert runner.state == []
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.state == 'DONE'
  assert runner.status[0][0] == 100.0
  assert runner.done
  runner.run()
  assert runner.state == 'DONE'
  assert runner.status[0][0] == 100.0
  assert runner.done

  runner = Runner( parse( 'begin()end' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done

  runner = Runner( parse( 'begin()end' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0


def test_values():
  runner = Runner( parse( 'myvar = 5' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 5 }

  runner = Runner( parse( 'myvar = "asdf"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 'asdf' }

  runner = Runner( parse( 'myvar = othervar' ) )
  assert runner.variable_map == {}
  runner.variable_map[ 'othervar' ] = 2.1
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'othervar': 2.1, 'myvar': 2.1 }

  runner = Runner( parse( 'thevar' ) )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'asdf = asdf' ) )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'adsf.asdf[1] = 123' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}


def test_array():
  runner = Runner( parse( 'myvar = []' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [] }

  runner = Runner( parse( 'myvar = [1,2,3]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ] }

  runner = Runner( parse( 'myvar = [1,(1+1),"asdf"]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, "asdf" ] }

  runner = Runner( parse( 'myvar = [1,2,3]\nasdf = myvar[2]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ], 'asdf': 3 }

  runner = Runner( parse( 'myvar = [1,2,3]\nasdf = myvar[ ( 1 + 1 ) ]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ], 'asdf': 3 }

  runner = Runner( parse( 'myvar = [1,2,3]\nappend( array=myvar, value=5 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3, 5 ] }

  runner = Runner( parse( 'myvar = [1,2,3]\nthelen = len( array=myvar )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ], 'thelen': 3 }

  runner = Runner( parse( 'myvar = [1,2,3,4,5,6,7,8]\nlittle = slice( array=myvar, start=2, end=4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3, 4, 5, 6, 7, 8 ], 'little': [ 3, 4 ] }

  runner = Runner( parse( 'myvar = [1,2,3,4,5,6,7,8]\nlittle = pop( array=myvar, index=1 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 3, 4, 5, 6, 7, 8 ], 'little': 2 }

  runner = Runner( parse( 'myvar = [1,2,3,4,5,6,7,8]\nlittle = index( array=myvar, value=4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3, 4, 5, 6, 7, 8 ], 'little': 3 }

  runner = Runner( parse( 'myvar = [1,2,3,4,5,6,7,8]\nmyvar[2] = "hello"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 'hello', 4, 5, 6, 7, 8 ] }

  runner = Runner( parse( 'myvar = [1,2,3,4,5,6,7,8]\nmyvar[ ( 1 + 3 ) ] = "by"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3, 4, 'by', 6, 7, 8 ] }

  runner = Runner( parse( 'myvar = [1,2,3,4,5,6,7,8]\nmyvar[ ( len( array=myvar ) - 1 ) ] = "end"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3, 4, 5, 6, 7, 'end' ] }

  runner = Runner( parse( 'myvar = [1,2,3,4,5]\nmyvar[ ( len( array=myvar ) - 1 ) ] = "end"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3, 4, 'end' ] }


def test_map():
  runner = Runner( parse( 'myvar = {}' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': {} }

  runner = Runner( parse( 'myvar = {aa=1,bb=2,cc=3}' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'aa': 1, 'bb': 2, 'cc': 3 } }

  runner = Runner( parse( 'myvar = { aa=1, bb=(1+1), cc="asdf" }' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'aa': 1, 'bb': 2, 'cc': "asdf" } }

  runner = Runner( parse( 'myvar = {aa=1,bb=2,cc=3}\nasdf = myvar["cc"]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'aa': 1, 'bb': 2, 'cc': 3 }, 'asdf': 3 }

  runner = Runner( parse( 'myvar = {aa=1,bb=2,cc=3}\nbob="bb"\nasdf = myvar[bob]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'aa': 1, 'bb': 2, 'cc': 3 }, 'asdf': 2, 'bob': 'bb' }

  runner = Runner( parse( 'myvar = {aa=1,bb=2,cc=3}\nthelen = len( array=myvar )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'aa': 1, 'bb': 2, 'cc': 3 }, 'thelen': 3 }

  runner = Runner( parse( 'myvar = {aa=1,bb=2,cc=3,dd=4,ee=5,ff=6}\nmyvar["cc"] = "hello"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'aa': 1, 'bb': 2, 'cc': 'hello', 'dd': 4, 'ee': 5, 'ff': 6 } }

  runner = Runner( parse( 'myvar = {aa=1,bb=2,cc=3,dd=4,ee=5,ff=6}\nbob = "ee"\nmyvar[ bob ] = "by"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'aa': 1, 'bb': 2, 'cc': 3, 'dd': 4, 'ee': 'by', 'ff': 6 }, 'bob': 'ee' }

  runner = Runner( parse( 'myvar = {}\nmyvar[ "hi" ] = "stuff"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': { 'hi': 'stuff' } }


def test_module_values():  # TODO: add pickling testing
  runner = Runner( parse( 'asdf = testing.bigstuff' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'asdf': 'the big stuff' }

  runner = Runner( parse( 'testing.littlestuff = 42' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == {}

  runner = Runner( parse( 'asdf = testing.otherstuff' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'asdf': None }

  runner = Runner( parse( 'asdf = testing.otherstuff\ntesting.otherstuff = "hello"\nqwerty = testing.otherstuff' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'asdf': None, 'qwerty': 'hello' }

  runner = Runner( parse( 'asdf = testing.bogus' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'testing.bogus = 100' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'asdf = bogus.bogus' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'bogus.bogus = 100' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}


def test_object_values():
  runner = Runner( parse( '' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )

  assert runner.object_list[0].dataRW == 'mod me'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'
  buff = pickle.dumps( runner )

  runner2 = pickle.loads( buff )
  assert runner2.object_list[0].dataRW == 'mod me'
  assert runner2.object_list[0].dataWO == 'write me'
  assert runner2.object_list[0].dataRO == 'read me'

  runner = Runner( parse( 'var = test_obj.dataRW' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.variable_map == { 'var': 'mod me' }
  assert runner.object_list[0].dataRW == 'mod me'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'

  runner = Runner( parse( 'var = test_obj.dataRO' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.variable_map == { 'var': 'read me' }
  assert runner.object_list[0].dataRW == 'mod me'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'

  runner = Runner( parse( 'var = test_obj.dataWO' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert runner.variable_map == {}
  assert runner.object_list[0].dataRW == 'mod me'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'

  runner = Runner( parse( 'var = "hi there"\ntest_obj.dataRW = var' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.variable_map == { 'var': 'hi there' }
  assert runner.object_list[0].dataRW == 'hi there'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'

  runner = Runner( parse( 'var = "hi there"\ntest_obj.dataRO = var' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert runner.variable_map == { 'var': 'hi there' }
  assert runner.object_list[0].dataRW == 'mod me'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'

  runner = Runner( parse( 'var = "hi there"\ntest_obj.dataWO = var' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.variable_map == { 'var': 'hi there' }
  assert runner.object_list[0].dataRW == 'mod me'
  assert runner.object_list[0].dataWO == 'hi there'
  assert runner.object_list[0].dataRO == 'read me'

  runner = Runner( parse( 'var = "iclke me pickle me tickle me too"\ntest_obj.dataRW = var' ) )
  runner.registerObject( testExternalObject( 'mod me', 'write me', 'read me' ) )
  assert runner.variable_map == {}
  assert runner.object_list[0].dataRW == 'mod me'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'
  buff = pickle.dumps( runner )
  runner2 = pickle.loads( buff )
  assert runner2.object_list[0].dataRW == 'mod me'
  assert runner2.object_list[0].dataWO == 'write me'
  assert runner2.object_list[0].dataRO == 'read me'
  runner.run()
  assert runner.variable_map == { 'var': 'iclke me pickle me tickle me too' }
  assert runner.object_list[0].dataRW == 'iclke me pickle me tickle me too'
  assert runner.object_list[0].dataWO == 'write me'
  assert runner.object_list[0].dataRO == 'read me'
  assert runner2.object_list[0].dataRW == 'mod me'
  assert runner2.object_list[0].dataWO == 'write me'
  assert runner2.object_list[0].dataRO == 'read me'
  buff = pickle.dumps( runner )
  runner3 = pickle.loads( buff )
  assert runner3.object_list[0].dataRW == 'iclke me pickle me tickle me too'
  assert runner3.object_list[0].dataWO == 'write me'
  assert runner3.object_list[0].dataRO == 'read me'


def test_infix():
  runner = Runner( parse( 'myvar = ( 1 + 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 3 }

  runner = Runner( parse( 'myvar = ( "1" . "2" )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': '12' }

  runner = Runner( parse( 'myvar = ( 1 - 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': -1 }

  runner = Runner( parse( 'myvar = ( 1 * 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 2 }

  runner = Runner( parse( 'myvar = ( 1.0 / 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 0.5 }

  runner = Runner( parse( 'myvar = ( 1 % 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 1 }

  runner = Runner( parse( 'myvar = ( 1 ^ 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 1 }

  runner = Runner( parse( 'myvar = ( 5 & 4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 4 }

  runner = Runner( parse( 'myvar = ( 5 | 4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 5 }

  runner = Runner( parse( 'myvar = ( 5 . "a" )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': '5a' }

  runner = Runner( parse( 'myvar = ( "a" . 2.0 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 'a2.0' }

  runner = Runner( parse( 'myvar = ( ( 1 + 3 ) . ( " d " . True ) )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': '4 d True' }

  runner = Runner( parse( 'myvar = ( 5 + "a" )' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'myvar = ( "a" + 2.0 )' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'myvar = ( True and False )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( parse( 'myvar = ( True or False )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( parse( 'myvar = ( 1 > 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( parse( 'myvar = ( 1 < 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( parse( 'myvar = ( 1 == 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( parse( 'myvar = ( 1 != 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( parse( 'myvar = ( 1 >= 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( parse( 'myvar = ( 1 <= 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( parse( 'test = 2\nmyvar = ( test + test )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'test': 2, 'myvar': 4 }

  runner = Runner( parse( 'myvar = ( 1 == 2 )\nvar2 = not myvar' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False, 'var2': True }

  runner = Runner( parse( 'var2 = not 0' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'var2': True }

  runner = Runner( parse( 'var2 = not 1' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'var2': False }


def test_pause_error():
  runner = Runner( parse( 'pause( msg="the message" )' ) )
  assert runner.variable_map == {}
  with pytest.raises( Pause ) as execinfo:
    runner.run()
  assert str( execinfo.value ) == 'the message'
  assert not runner.done
  assert not runner.aborted
  assert runner.run() == ''
  assert runner.done
  assert not runner.aborted
  assert runner.run() == 'done'
  assert runner.variable_map == {}

  runner = Runner( parse( 'error( msg="oops fix it" )' ) )
  assert runner.variable_map == {}
  with pytest.raises( ExecutionError ) as execinfo:
    runner.run()
  assert str( execinfo.value ) == 'oops fix it'
  assert not runner.done
  assert not runner.aborted
  assert runner.run() == ''
  assert runner.done
  assert not runner.aborted
  assert runner.run() == 'done'
  assert runner.variable_map == {}

  runner = Runner( parse( 'fatal_error( msg="the world is over, go home" )' ) )
  assert runner.variable_map == {}
  with pytest.raises( UnrecoverableError ) as execinfo:
    runner.run()
  assert str( execinfo.value ) == 'the world is over, go home'
  assert not runner.done
  assert runner.aborted
  assert runner.run() == 'aborted'
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'pause( msg="you should do something" )\nerror( msg="seriously do it" )\nfatal_error( msg="to late now" )' ) )
  assert runner.variable_map == {}
  with pytest.raises( Pause ) as execinfo:
    runner.run()
  assert str( execinfo.value ) == 'you should do something'
  assert not runner.done
  assert not runner.aborted
  with pytest.raises( ExecutionError ) as execinfo:
    runner.run()
  assert str( execinfo.value ) == 'seriously do it'
  assert not runner.done
  assert not runner.aborted
  with pytest.raises( UnrecoverableError ) as execinfo:
    runner.run()
  assert str( execinfo.value ) == 'to late now'
  assert not runner.done
  assert runner.aborted
  assert runner.run() == 'aborted'
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}


def test_builtin_functions():
  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nvar = len( array=ary )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': 4 }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\n333\nvar = len( array=ary )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': 4 }

  runner = Runner( parse( '333\nary = [ 1,2,3,4 ]\n333\nvar = len( array=ary )\n333' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': 4 }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nvar = slice( array=ary, start=2, end=3 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': [ 3 ] }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nvar = slice( array=ary, start=0, end=2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': [ 1, 2 ] }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nvar = pop( array=ary, index=0 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 2, 3, 4 ], 'var': 1 }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nvar = pop( array=ary, index=-1 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3 ], 'var': 4 }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nvar = pop( array=ary )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3 ], 'var': 4 }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nappend( array=ary, value=5 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4, 5 ] }

  runner = Runner( parse( 'ary = [ 1,2,3,4 ]\nvar = index( array=ary, value=3 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': 2 }


def test_delay():
  runner = Runner( parse( 'delay( seconds=5 )' ) )
  assert runner.run() == 'Waiting for 4 more seconds'
  assert runner.done is False
  time.sleep( 1 )
  assert runner.run() == 'Waiting for 3 more seconds'
  assert runner.done is False
  time.sleep( 5 )
  runner.run()
  assert runner.done

  runner = Runner( parse( 'delay( minutes=5 )' ) )
  assert runner.run() == 'Waiting for 299 more seconds'
  assert runner.done is False
  time.sleep( 1 )
  assert runner.run() == 'Waiting for 298 more seconds'

  runner = Runner( parse( 'delay( hours=2 )' ) )
  assert runner.run() == 'Waiting for 7199 more seconds'
  assert runner.done is False
  time.sleep( 2 )
  assert runner.run() == 'Waiting for 7197 more seconds'


def test_message():
  runner = Runner( parse( 'message( msg="Hello World" )' ) )
  assert runner.run() == 'Hello World'
  assert not runner.done
  assert runner.run() == ''
  assert runner.done


def test_object_functions():  # TODO: this and pickleing too
  pass


def test_module_functions():
  runner = Runner( parse( 'var = testing.constant()' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 42 }

  runner = Runner( parse( 'var = testing.multiply( value=4321 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 43210 }

  runner = Runner( parse( 'var = testing.multiply( value=4321 )\nvar2 = testing.multiply( value=12 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 43210, 'var2': 120 }

  runner = Runner( parse( 'var = ( testing.multiply( value=2 ) + testing.multiply( value=3 ) )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 50 }

  runner = Runner( parse( 'var = testing.multiply( value=testing.multiply( value=11 ) )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 1100 }

  runner = Runner( parse( '321\nvar = testing.multiply( value=testing.multiply( value=11 ) )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 1100 }

  runner = Runner( parse( 'testing.count( stop_at=2, count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  assert runner.run() == 'at 1 of 2'
  assert runner.status[0][0] == 0.0
  assert not runner.done
  assert runner.run() == 'at 2 of 2'
  assert runner.status[0][0] == 0.0
  assert not runner.done
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'

  runner = Runner( parse( 'testing.count( stop_at="asd", count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.run() == 'aborted'
  assert runner.status[0][0] == 100.0

  runner = Runner( parse( 'testing.count( stop_at=2, count_by=1 )\ntesting.count( stop_at=1, count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  assert runner.run() == 'at 1 of 2'
  assert runner.status[0][0] == 0.0
  assert not runner.done
  assert runner.run() == 'at 2 of 2'
  assert not runner.done
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'count', 'dispatched': False } ) ]
  assert runner.run() == 'at 1 of 1'
  assert not runner.done
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'count', 'dispatched': False } ) ]
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'


def test_external_remote_functions():
  runner = Runner( parse( 'testing.remote()' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.line == 0
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Script not Running', None )
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Not Expecting Anything', None )
  assert runner.toSubcontractor( [] ) is None
  assert runner.toSubcontractor( [ 'sdf', 'were' ] ) is None
  assert runner.toSubcontractor( [ 'rfrf', 'testing', 'sdf' ] ) == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote_func', 'paramaters': 'the count "1"' }
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': True } ) ]
  assert runner.line == 1
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': True } ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.fromSubcontractor( 'Bad Cookie', True ) == ( 'Bad Cookie', None )
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Accepted', 'Current State "True"' )
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Not Expecting Anything', None )
  assert runner.toSubcontractor( [ 'testing' ] ) == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote_func', 'paramaters': 'the count "2"' }
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': True } ) ]
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Accepted', 'Current State "True"' )
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.run() == ''
  assert runner.done
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Script not Running', None )
  assert runner.run() == 'done'
  assert runner.line is None
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None

  runner = Runner( parse( 'var1 = testing.remote()' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.variable_map == {}
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote_func', 'paramaters': 'the count "1"' }
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': True } ) ]
  assert runner.variable_map == {}
  assert runner.fromSubcontractor( runner.contractor_cookie, 'the sky is falling' ) == ( 'Accepted', 'Current State "the sky is falling"' )
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.variable_map == {}
  assert runner.run() == ''
  assert runner.done
  assert runner.run() == 'done'
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.variable_map == { 'var1': 'the sky is falling' }

  runner = Runner( parse( 'testing.remote()' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.variable_map == {}
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote_func', 'paramaters': 'the count "1"' }
  assert runner.variable_map == {}
  assert runner.fromSubcontractor( runner.contractor_cookie, 'Bad' ) == ( 'Accepted', 'Current State "Bad"' )
  assert runner.variable_map == {}
  with pytest.raises( UnrecoverableError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.run() == 'aborted'
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.variable_map == {}
# TODO: test function rollback


def test_serilizer():
  runner = Runner( parse( 'testing.count( stop_at=2, count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 0.0
  assert not runner.done
  runner.run()
  assert runner.status[0][0] == 0.0
  assert not runner.done
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done

  runner = Runner( parse( 'testing.count( stop_at=2, count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 0.0
  assert not runner.done

  buff = pickle.dumps( runner )
  # origional sould  play out as normal
  runner.run()
  assert runner.status[0][0] == 0.0
  assert not runner.done
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done

  # copy should do the same thing
  runner2 = pickle.loads( buff )
  runner2.run()
  assert runner2.status[0][0] == 0.0
  assert not runner2.done
  runner2.run()
  assert runner2.status[0][0] == 100.0
  assert runner2.done


def test_while():
  # first we will test the ttl
  runner = Runner( parse( 'while True do 1' ) )
  assert runner.status[0][0] == 0.0
  with pytest.raises( Timeout ):
    runner.run( 0 )
  assert runner.status[0][0] == 0.0
  assert not runner.done

  # ok, now we can have some fun
  runner = Runner( parse( 'while True do 1' ) )
  assert runner.status[0][0] == 0.0
  with pytest.raises( Timeout ):
    runner.run( 10 )
  assert runner.status[0][0] == 0.0
  assert not runner.done

  runner = Runner( parse( 'cnt = 1\nwhile ( cnt >= 1 ) do cnt = ( cnt + 1 )' ) )
  assert runner.status[0][0] == 0.0
  for i in range( 0, 100 ):  # just do this infinite loop for a long time, make sure it dosen't have other problems
    with pytest.raises( Timeout ):
      runner.run( i )
    runner.status  # make sure nothing bad happens while computing status
  assert runner.status[0][0] == 50.0
  assert not runner.done

  runner = Runner( parse( 'cnt = 1\nwhile True do cnt = ( cnt + 1 )' ) )
  assert runner.status[0][0] == 0.0
  with pytest.raises( Timeout ):
    runner.run( 20 )
  assert runner.status[0][0] == 50.0
  assert not runner.done
  assert runner.variable_map == { 'cnt': 3 }
  with pytest.raises( Timeout ):
    runner.run( 20 )
  assert runner.status[0][0] == 50.0
  assert not runner.done
  assert runner.variable_map == { 'cnt': 6 }

  runner = Runner( parse( 'while False do asdf = 5' ) )
  assert runner.status[0][0] == 0.0
  runner.run( 500 )
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == {}

  runner = Runner( parse( 'cnt = 1\nwhile ( cnt < 10 ) do cnt = ( cnt + 1 )' ) )
  assert runner.status[0][0] == 0.0
  runner.run( 500 )
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'cnt': 10 }


def test_ifelse():
  runner = Runner( parse( 'if False then var = 1' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == {}

  runner = Runner( parse( 'if True then var = 1' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'var': 1 }

  runner = Runner( parse( 'if False then var = 1 else var = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'var': 2 }

  runner = Runner( parse( 'asd = 1\nif ( asd == 1 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 3 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "a" }

  runner = Runner( parse( 'asd = 2\nif ( asd == 1 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 3 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 2, 'var': "b" }

  runner = Runner( parse( 'asd = 9\nif ( asd == 1 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 3 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 9, 'var': "d" }

  runner = Runner( parse( 'asd = 1\nif ( asd == 1 ) then var = "a" elif ( asd == 1 ) then var = "b" elif ( asd == 1 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "a" }

  runner = Runner( parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 1 ) then var = "b" elif ( asd == 1 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "b" }

  runner = Runner( parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 1 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "c" }

  runner = Runner( parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 2 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "d" }

  runner = Runner( parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 2 ) then var = "c" else var = "d"\nwhile True do 10' ) )
  assert runner.status[0][0] == 0.0
  for i in range( 0, 10 ):  # just do this infinite loop for a long time, make sure it dosen't have other problems
    with pytest.raises( Timeout ):
      runner.run( i )
    runner.status  # make sure nothing bad happens while computing status
  assert runner.status[0][0] == 66.66666666666667
  assert not runner.done


def test_jumppoint():
  runner = Runner( parse( 'abc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'abc': 1, 'dce': 2 }

  runner = Runner( parse( 'goto jump_a\nabc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

  runner = Runner( parse( 'goto jump_a\nabc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

  runner = Runner( parse( 'goto jump_b\nabc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert runner.status[0][0] == 100.0
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( parse( 'goto jump_b\nabc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.goto( 'jump_a' )
  with pytest.raises( Timeout ):
    runner.run( 2 )
  assert runner.line == 3
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

  runner = Runner( parse( 'goto jump_b\nabc = 1\ndelay( seconds=1 )\n:jump_b\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

  runner = Runner( parse( 'goto jump_b\nbegin()\nabc = 1\nend\n:jump_b\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

  runner = Runner( parse( 'begin()\ngoto jump_b\nabc = 1\nend\n:jump_b\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

# test jumping over one function to another, making sure that the function returns are not crossed, and the jumped over function dosen't get it's return value accepted
# test the contractor_cookie is getting rolled over correctly
# try something with a better progress
# test serilize and unserilize, especially with all the block options
# test getting status, going to need a function that can paus executeion both for the value and also for the index


def test_status():
  runner = Runner( parse( 'begin()\n42\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'pause( msg="" )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( '42\npause( msg="" )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'pause( msg="1" )\npause( msg="2" )\npause( msg="3" )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 33.333333333333336, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 66.66666666666667, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done
  runner = Runner( parse( 'begin()\npause( msg="" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'begin()\n42\npause( msg="" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( '12\nbegin()\n42\npause( msg="" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 75.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( '12\nbegin()\n42\npause( msg="" )\nend\n34' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'while True do pause( msg="" )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'expression' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'expression' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done

  runner = Runner( parse( 'while True do begin()\n5\npause( msg="" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'While', { 'doing': 'expression' } ), ( 50.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'While', { 'doing': 'expression' } ), ( 50.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done

  runner = Runner( parse( 'while True do begin()\n5\npause( msg="" )\n6\npause( msg="" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 25.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 25.0, 'While', { 'doing': 'expression' } ), ( 25.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 75.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 75.0, 'While', { 'doing': 'expression' } ), ( 75.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done

  runner = Runner( parse( 'while pause( msg="" ) do 5' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'while not pause( msg="" ) do 5' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done

  runner = Runner( parse( '( not pause( msg="cond" ) | True )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( '( True | not pause( msg="cond" ) )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'while not pause( msg="cond" ) do begin()\npause( msg="exp" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'expression' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'expression' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done

  runner = Runner( parse( 'while not pause( msg="cond" ) do begin()\n12\npause( msg="exp" )\n34\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 33.333333333333336, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 33.333333333333336, 'While', { 'doing': 'expression' } ), ( 33.333333333333336, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'While', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 33.333333333333336, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 33.333333333333336, 'While', { 'doing': 'expression' } ), ( 33.333333333333336, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done

  runner = Runner( parse( 'if True then pause( msg="exp" )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'IfElse', { 'doing': 'expression' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'if pause( msg="cond" ) then 5' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'IfElse', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'if not pause( msg="cond" ) then 5' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'IfElse', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'if False then 23 else pause( msg="cond" )' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'IfElse', { 'doing': 'expression' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'if not pause( msg="cond" ) then begin()\npause( msg="exp" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'IfElse', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'IfElse', { 'doing': 'expression' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'if False then 1 elif not pause( msg="cond" ) then begin()\npause( msg="exp" )\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'IfElse', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'IfElse', { 'doing': 'expression' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'if False then 1 elif not pause( msg="cond" ) then begin()\n5\npause( msg="exp" )\n6\nend' ) )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 50.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 50.0, 'IfElse', { 'doing': 'condition' } ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 66.66666666666667, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 66.66666666666667, 'IfElse', { 'doing': 'expression' } ), ( 33.333333333333336, 'Scope', {} ), ( 0.0, 'Function', { 'module': None, 'name': 'pause' } ) ]
  assert not runner.done
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done


def test_exists():
  runner = Runner( parse( 'aa = 1' ) )
  runner.run()
  assert runner.variable_map == { 'aa': 1 }

  runner = Runner( parse( 'aa = bb' ) )
  with pytest.raises( NotDefinedError ):
    runner.run()

  runner = Runner( parse( 'aa = exists( bb )' ) )
  runner.run()
  assert runner.variable_map == { 'aa': False }

  runner = Runner( parse( 'bb = 1\naa = exists( bb )' ) )
  runner.run()
  assert runner.variable_map == { 'aa': True, 'bb': 1 }

  runner = Runner( parse( 'bb = [ 1, 2 ]\naa = exists( bb )' ) )
  runner.run()
  assert runner.variable_map == { 'aa': True, 'bb': [ 1, 2 ] }

  runner = Runner( parse( 'bb = [ 1, 2 ]\naa = exists( bb[ 3 ] )' ) )
  runner.run()
  assert runner.variable_map == { 'aa': False, 'bb': [ 1, 2 ] }


def test_block_timing():
  runner = Runner( parse( 'begin( expected_time=0:10 )\ndelay( seconds=4 )\nend' ) )
  assert runner.run() == 'Waiting for 3 more seconds'
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:09' } ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert not runner.done

  time.sleep( 2 )
  assert runner.run() == 'Waiting for 1 more seconds'
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:02', 'time_remaining': '00:07' } ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert runner.done is False

  time.sleep( 2 )
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'begin( expected_time=0:02 )\ndelay( seconds=8 )\nend' ) )
  assert runner.run() == 'Waiting for 7 more seconds'
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:01' } ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert not runner.done

  time.sleep( 4 )
  assert runner.run() == 'Waiting for 3 more seconds'
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:04', 'time_remaining': '-00:02' } ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert runner.done is False

  time.sleep( 4 )
  runner.run()
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.done

  runner = Runner( parse( 'begin( max_time=0:03 )\ndelay( seconds=6 )\nend' ) )
  assert runner.run() == 'Waiting for 5 more seconds'
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert not runner.done

  time.sleep( 2 )
  assert runner.run() == 'Waiting for 3 more seconds'
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert not runner.done

  time.sleep( 2 )
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert not runner.done

  assert runner.run() == 'Waiting for 1 more seconds'
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert not runner.done

  time.sleep( 2 )
  with pytest.raises( Pause ):
    runner.run()
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', {} ), ( 0.0, 'Function', { 'dispatched': False, 'module': None, 'name': 'delay' } ) ]
  assert not runner.done

  runner.run()
  assert runner.done


def test_block_timing_with_remote():
  runner = Runner( parse( 'begin( expected_time=0:10 )\ntesting.remote()\nend' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status == [ ( 0.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.line == 0
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Script not Running', None )
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:09' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Not Expecting Anything', None )
  assert runner.toSubcontractor( [] ) is None
  assert runner.toSubcontractor( [ 'sdf', 'were' ] ) is None
  assert runner.toSubcontractor( [ 'rfrf', 'testing', 'sdf' ] ) == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote_func', 'paramaters': 'the count "1"' }
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:09' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': True } ) ]
  assert runner.line == 2
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:09' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': True } ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.fromSubcontractor( 'Bad Cookie', True ) == ( 'Bad Cookie', None )
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Accepted', 'Current State "True"' )
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:09' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Not Expecting Anything', None )
  assert runner.toSubcontractor( [ 'testing' ] ) == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote_func', 'paramaters': 'the count "2"' }
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:09' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': True } ) ]
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Accepted', 'Current State "True"' )
  assert runner.status == [ ( 0.0, 'Scope', { 'description': 'Overall Script', 'time_elapsed': '00:00' } ), ( 0.0, 'Scope', { 'time_elapsed': '00:00', 'time_remaining': '00:09' } ), ( 0.0, 'Function', { 'module': 'testing', 'name': 'remote', 'dispatched': False } ) ]
  assert runner.run() == ''
  assert runner.done
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == ( 'Script not Running', None )
  assert runner.run() == 'done'
  assert runner.line is None
  assert runner.status == [ ( 100.0, 'Scope', None ) ]
  assert runner.toSubcontractor( [ 'testing' ] ) is None
