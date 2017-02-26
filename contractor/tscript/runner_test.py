import pytest
import pickle
from datetime import timedelta

from contractor.tscript.parser import parse
from contractor.tscript.runner import Runner, ExecutionError, UnrecoverableError, ParamaterError, NotDefinedError, Timeout, Pause

class TestStructure( object ):
  pass


def test_begin():
  struct = TestStructure()

  runner = Runner( struct, parse( '' ) )
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

  runner = Runner( struct, parse( 'begin()end' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done

  runner = Runner( struct, parse( 'begin()end' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0


def test_values():
  struct = TestStructure()

  runner = Runner( struct, parse( 'myvar = 5' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 5 }

  runner = Runner( struct, parse( 'myvar = "asdf"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 'asdf' }

  runner = Runner( struct, parse( 'myvar = othervar' ) )
  assert runner.variable_map == {}
  runner.variable_map[ 'othervar' ] = 2.1
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'othervar': 2.1, 'myvar': 2.1 }

  runner = Runner( struct, parse( 'thevar' ) )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'asdf = asdf' ) )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'adsf.asdf[1] = 123' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}


def test_array():
  struct = TestStructure()

  runner = Runner( struct, parse( 'myvar = []' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [] }

  runner = Runner( struct, parse( 'myvar = [1,2,3]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ] }

  runner = Runner( struct, parse( 'myvar = [1,(1+1),"asdf"]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, "asdf" ] }

  runner = Runner( struct, parse( 'myvar = [1,2,3]\nasdf = myvar[2]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ], 'asdf': 3 }

  runner = Runner( struct, parse( 'myvar = [1,2,3]\nasdf = myvar[ ( 1 + 1 ) ]' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ], 'asdf': 3 }

  runner = Runner( struct, parse( 'myvar = [1,2,3]\nappend( array=myvar, value=5 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3, 5 ] }

  runner = Runner( struct, parse( 'myvar = [1,2,3]\nthelen = len( array=myvar )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [ 1, 2, 3 ], 'thelen': 3 }

  runner = Runner( struct, parse( 'myvar = [1,2,3,4,5,6,7,8]\nlittle = slice( array=myvar, start=2, end=4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [1,2,3,4,5,6,7,8], 'little': [ 3,4] }

  runner = Runner( struct, parse( 'myvar = [1,2,3,4,5,6,7,8]\nlittle = pop( array=myvar, index=1 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [1,3,4,5,6,7,8], 'little': 2 }

  runner = Runner( struct, parse( 'myvar = [1,2,3,4,5,6,7,8]\nlittle = index( array=myvar, value=4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [1,2,3,4,5,6,7,8], 'little': 3 }

  runner = Runner( struct, parse( 'myvar = [1,2,3,4,5,6,7,8]\nmyvar[2] = "hello"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [1,2,'hello',4,5,6,7,8] }

  runner = Runner( struct, parse( 'myvar = [1,2,3,4,5,6,7,8]\nmyvar[ ( 1 + 3 ) ] = "by"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [1,2,3,4,'by',6,7,8] }

  runner = Runner( struct, parse( 'myvar = [1,2,3,4,5,6,7,8]\nmyvar[ ( len( array=myvar ) - 1 ) ] = "end"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [1,2,3,4,5,6,7,'end'] }

  runner = Runner( struct, parse( 'myvar = [1,2,3,4,5]\nmyvar[ ( len( array=myvar ) - 1 ) ] = "end"' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': [1,2,3,4,'end'] }


def test_plugin_values():
  struct = TestStructure()

  runner = Runner( struct, parse( 'asdf = testing.bigstuff' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'asdf': 'the big stuff' }

  runner = Runner( struct, parse( 'testing.littlestuff = 42' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'asdf = testing.otherstuff' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'asdf': None }

  runner = Runner( struct, parse( 'asdf = testing.otherstuff\ntesting.otherstuff = "hello"\nqwerty = testing.otherstuff' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'asdf': None, 'qwerty': 'hello' }

  runner = Runner( struct, parse( 'asdf = testing.bogus' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'testing.bogus = 100' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'asdf = bogus.bogus' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'bogus.bogus = 100' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}


def test_infix():
  struct = TestStructure()

  runner = Runner( struct, parse( 'myvar = ( 1 + 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 3 }

  runner = Runner( struct, parse( 'myvar = ( 1 - 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': -1 }

  runner = Runner( struct, parse( 'myvar = ( 1 * 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 2 }

  runner = Runner( struct, parse( 'myvar = ( 1.0 / 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 0.5 }

  runner = Runner( struct, parse( 'myvar = ( 1 % 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 1 }

  runner = Runner( struct, parse( 'myvar = ( 1 ^ 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 1 }

  runner = Runner( struct, parse( 'myvar = ( 5 & 4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 4 }

  runner = Runner( struct, parse( 'myvar = ( 5 | 4 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': 5 }

  runner = Runner( struct, parse( 'myvar = ( 5 + "a" )' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'myvar = ( "a" + 2.0 )' ) )
  assert runner.variable_map == {}
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'myvar = ( True and False )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( struct, parse( 'myvar = ( True or False )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( struct, parse( 'myvar = ( 1 > 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( struct, parse( 'myvar = ( 1 < 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( struct, parse( 'myvar = ( 1 == 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( struct, parse( 'myvar = ( 1 != 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( struct, parse( 'myvar = ( 1 >= 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False }

  runner = Runner( struct, parse( 'myvar = ( 1 <= 2 )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': True }

  runner = Runner( struct, parse( 'test = 2\nmyvar = ( test + test )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'test': 2, 'myvar': 4 }

  runner = Runner( struct, parse( 'myvar = ( 1 == 2 )\nvar2 = not myvar' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'myvar': False, 'var2': True }

  runner = Runner( struct, parse( 'var2 = not 0' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'var2': True }

  runner = Runner( struct, parse( 'var2 = not 1' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'var2': False }


def test_pause_error():
  struct = TestStructure()

  runner = Runner( struct, parse( 'pause( msg="the message" )' ) )
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

  runner = Runner( struct, parse( 'error( msg="oops fix it" )' ) )
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

  runner = Runner( struct, parse( 'fatal_error( msg="the world is over, go home" )' ) )
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

  runner = Runner( struct, parse( 'pause( msg="you should do something" )\nerror( msg="seriously do it" )\nfatal_error( msg="to late now" )' ) )
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


def test_functions():
  struct = TestStructure()

  runner = Runner( struct, parse( 'ary = [ 1,2,3,4 ]\nvar = len( array=ary )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': 4 }

  runner = Runner( struct, parse( 'ary = [ 1,2,3,4 ]\n333\nvar = len( array=ary )' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': 4 }

  runner = Runner( struct, parse( '333\nary = [ 1,2,3,4 ]\n333\nvar = len( array=ary )\n333' ) )
  assert runner.variable_map == {}
  runner.run()
  assert runner.done
  assert runner.variable_map == { 'ary': [ 1, 2, 3, 4 ], 'var': 4 }


def test_external_functions():
  struct = TestStructure()

  runner = Runner( struct, parse( 'var = testing.constant()' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 42 }

  runner = Runner( struct, parse( 'var = testing.multiply( value=4321 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 43210 }

  runner = Runner( struct, parse( 'var = testing.multiply( value=4321 )\nvar2 = testing.multiply( value=12 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 43210,  'var2': 120 }

  runner = Runner( struct, parse( 'var = ( testing.multiply( value=2 ) + testing.multiply( value=3 ) )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 50 }

  runner = Runner( struct, parse( 'var = testing.multiply( value=testing.multiply( value=11 ) )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 1100 }

  runner = Runner( struct, parse( '321\nvar = testing.multiply( value=testing.multiply( value=11 ) )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.variable_map == {}
  assert runner.status[0][0] == 0.0
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'
  assert runner.variable_map == { 'var': 1100 }

  runner = Runner( struct, parse( 'testing.count( stop_at=2, count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  assert runner.run() == 'at 0 of 2'
  assert runner.status[0][0] == 0.0
  assert not runner.done
  assert runner.run() == 'at 1 of 2'
  assert runner.status[0][0] == 0.0
  assert not runner.done
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'

  runner = Runner( struct, parse( 'testing.count( stop_at="asd", count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  with pytest.raises( ParamaterError ):
    runner.run()
  assert not runner.done
  assert runner.aborted
  assert runner.run() == 'aborted'
  assert runner.status[0][0] == 100.0

  runner = Runner( struct, parse( 'testing.count( stop_at=2, count_by=1 )\ntesting.count( stop_at=1, count_by=1 )' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status[0][0] == 0.0
  assert runner.run() == 'at 0 of 2'
  assert runner.status[0][0] == 0.0
  assert not runner.done
  assert runner.run() == 'at 1 of 2'
  assert not runner.done
  assert runner.status == [ ( 0.0, {} ) ]
  assert runner.run() == 'at 0 of 1'
  assert not runner.done
  assert runner.status == [ ( 50.0, {} ) ]
  assert runner.run() == ''
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.run() == 'done'


def test_external_remote_functions():
  struct = TestStructure()

  runner = Runner( struct, parse( 'testing.remote()' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status == [ ( 0.0, None ) ]
  assert runner.toSubcontractor() == None
  assert runner.line == 0
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, {} ) ]
  assert runner.toSubcontractor() == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote', 'paramaters': 'the count "1"' }
  assert runner.line == 1
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, {} ) ]
  assert runner.toSubcontractor() == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote', 'paramaters': 'the count "2"' }
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, {} ) ]
  assert runner.toSubcontractor() == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote', 'paramaters': 'the count "3"' }
  assert runner.fromSubcontractor( runner.contractor_cookie, True ) == 3
  assert runner.run() == ''
  assert runner.done
  assert runner.run() == 'done'
  assert runner.line == None
  assert runner.status == [ ( 100.0, None ) ]
  assert runner.toSubcontractor() == None

  runner = Runner( struct, parse( 'var1 = testing.remote()' ) )
  runner.registerModule( 'contractor.tscript.runner_plugins_test' )
  assert runner.status == [ ( 0.0, None ) ]
  assert runner.toSubcontractor() == None
  assert runner.variable_map == {}
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, {} ) ]
  assert runner.toSubcontractor() == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote', 'paramaters': 'the count "1"' }
  assert runner.variable_map == {}
  assert runner.run() == 'Not Initilized'
  assert not runner.done
  assert runner.status == [ ( 0.0, {} ) ]
  assert runner.toSubcontractor() == { 'cookie': runner.contractor_cookie, 'module': 'testing', 'function': 'remote', 'paramaters': 'the count "2"' }
  assert runner.variable_map == {}
  assert runner.fromSubcontractor( runner.contractor_cookie, 'the sky is falling' ) == 2
  assert runner.variable_map == {}
  assert runner.run() == ''
  assert runner.done
  assert runner.run() == 'done'
  assert runner.status == [ ( 100.0, None ) ]
  assert runner.toSubcontractor() == None
  assert runner.variable_map == { 'var1': 'the sky is falling' }


def test_serilizer():
  struct = TestStructure()

  runner = Runner( struct, parse( 'testing.count( stop_at=2, count_by=1 )' ) )
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

  runner = Runner( struct, parse( 'testing.count( stop_at=2, count_by=1 )' ) )
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
  struct = TestStructure()

  # first we will test the ttl
  runner = Runner( struct, parse( 'while True do 1' ) )
  assert runner.status[0][0] == 0.0
  with pytest.raises( Timeout ):
    runner.run( 0 )
  assert runner.status[0][0] == 0.0
  assert not runner.done

  # ok, now we can have some fun
  runner = Runner( struct, parse( 'while True do 1' ) )
  assert runner.status[0][0] == 0.0
  with pytest.raises( Timeout ):
    runner.run( 10 )
  assert runner.status[0][0] == 0.0
  assert not runner.done

  runner = Runner( struct, parse( 'cnt = 1\nwhile ( cnt >= 1 ) do cnt = ( cnt + 1 )' ) )
  assert runner.status[0][0] == 0.0
  for i in range( 0, 100 ): # just do this infinite loop for a long time, make sure it dosen't have other problems
    with pytest.raises( Timeout ):
      runner.run( i )
    runner.status # make sure nothing bad happens while computing status
  assert runner.status[0][0] == 50.0
  assert not runner.done

  runner = Runner( struct, parse( 'cnt = 1\nwhile True do cnt = ( cnt + 1 )' ) )
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

  runner = Runner( struct, parse( 'while False do asdf = 5' ) )
  assert runner.status[0][0] == 0.0
  runner.run( 500 )
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'cnt = 1\nwhile ( cnt < 10 ) do cnt = ( cnt + 1 )' ) )
  assert runner.status[0][0] == 0.0
  runner.run( 500 )
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'cnt': 10 }

def test_ifelse():
  struct = TestStructure()

  runner = Runner( struct, parse( 'if False then var = 1' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'if True then var = 1' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'var': 1 }

  runner = Runner( struct, parse( 'if False then var = 1 else var = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'var': 2 }

  runner = Runner( struct, parse( 'asd = 1\nif ( asd == 1 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 3 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "a" }

  runner = Runner( struct, parse( 'asd = 2\nif ( asd == 1 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 3 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 2, 'var': "b" }

  runner = Runner( struct, parse( 'asd = 9\nif ( asd == 1 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 3 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 9, 'var': "d" }

  runner = Runner( struct, parse( 'asd = 1\nif ( asd == 1 ) then var = "a" elif ( asd == 1 ) then var = "b" elif ( asd == 1 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "a" }

  runner = Runner( struct, parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 1 ) then var = "b" elif ( asd == 1 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "b" }

  runner = Runner( struct, parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 1 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "c" }

  runner = Runner( struct, parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 2 ) then var = "c" else var = "d"' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'asd': 1, 'var': "d" }

  runner = Runner( struct, parse( 'asd = 1\nif ( asd == 2 ) then var = "a" elif ( asd == 2 ) then var = "b" elif ( asd == 2 ) then var = "c" else var = "d"\nwhile True do 10' ) )
  assert runner.status[0][0] == 0.0
  for i in range( 0, 10 ): # just do this infinite loop for a long time, make sure it dosen't have other problems
    with pytest.raises( Timeout ):
      runner.run( i )
    runner.status # make sure nothing bad happens while computing status
  assert runner.status[0][0] == 66.66666666666667
  assert not runner.done

def test_jumppoint():
  struct = TestStructure()

  runner = Runner( struct, parse( 'abc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'abc': 1, 'dce': 2 }

  runner = Runner( struct, parse( 'goto jump_a\nabc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

  runner = Runner( struct, parse( 'goto jump_b\nabc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  with pytest.raises( NotDefinedError ):
    runner.run()
  assert runner.status[0][0] == 100.0
  assert not runner.done
  assert runner.aborted
  assert runner.variable_map == {}

  runner = Runner( struct, parse( 'goto jump_b\nabc = 1\n:jump_a\ndce = 2' ) )
  assert runner.status[0][0] == 0.0
  runner.goto( 'jump_a' )
  with pytest.raises( Timeout ):
    runner.run( 2 )
  assert runner.line == 3
  runner.run()
  assert runner.status[0][0] == 100.0
  assert runner.done
  assert runner.variable_map == { 'dce': 2 }

#test jumping over a blocking function
# test jumping over one function to another, making sure that the function returns are not crossed, and the jumped over function dosen't get it's return value accepted
#test the contractor_cookie is getting rolled over correctly
#try something with a better progress
# test serilize and unserilize, especially with all the block options
