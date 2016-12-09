import pytest
from datetime import timedelta

from contractor.tscript.parser import parse
from contractor.tscript.runner import run, ExternnalFunction, ExecutionError, UnrecoverableError, ParamaterError

class constant_func( ExternnalFunction ):
  def return_value( self ):
    return 42

class multiply_func( ExternalFunction ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.value = 0
    
  def execute( self, parms ):
    try:
       self.value = int( paramaters[ 'value' ] )
    except ( KeyError, ValueError ):
      raise ParamaterError( 'value', 'not provided or is not an int' )
      
  def return_value( self ):
    return self.value * 10

class delay_func( ExternnalFunction ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.end_at = None
  
  def ready( self ):
    if self.end_at is None:
      return 'Not Initilized'
    
    if datetime.now() >= self.end_at:
      return True
      
    else:
      return '{0} more seconds'.format( self.end_at - datetime.now() )

  def execute( self, parms ):
    try:
      self.end_at = datetime.now() + int( parms[ 'delay' ] )
    except ( KeyError, ValueError ):
      raise ParamaterError( 'delay', 'not provided or is not an int' )

def test_begin():
  node = parse( '' )
