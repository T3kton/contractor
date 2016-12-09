#now run that stuff

class ExecutionError( Exception ):
  pass

class UnrecoverableError( Exception ):
  pass

class ParamaterError( UnrecoverableError ):
  def __init__( self, name, msg ):
    super.__init__()
    self.name = name
    self.msg = msg

# for an inline non-pausing/remote function, you only need to implement execute and return_value, to_contractor is not called if ready is immeditally True.

# any exceptions raised in any of these functions will cause the job the script is running for to end up in error state. Use the any Excpetions other than 
# ExecutionError and UnrecoverableError will have it's Exception Name displayed in the output... where possible use ExecutionError for "normal" errors.
# UnrecoverableError will case the Job to enter a perminate Error state where the job can not be resumed.

class ExternnalFunction( object ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    
  def ready( self ):
    # this is called every time contractor wants to know if this script can continue.  
    # True -> can continue, no error, False -> can not continue, anything else, is treated as a status message and is displaied (otherwise treated as False)
    # it is probably wise that this funcion does not do any processing, it may be call multiple times with out any other function in the class being called.
    # do not depend on return_value being called imeditally after ready returns True, ready may have to return True multiple times before the return_value is 
    # reterieved and the object is cleaned up.  It is also possible that ready may still be called after return_value is reterieved.
    # NOTE: if ready ever returns True, it can not take that back, bad things may happen.  Including trowing exceptions, they will probably be ignored.
    return True
  
  def return_value( self ):
    # this returns the return value of this function, called only once, after ready returns True
    return None
  
  def execute( self, parms ):
    # this function is only called once when the function is first called in the script.
    # parms is a dict of the paramaters passed in from the script
    # if the params are not wnat they should be,  raise ParamaterError
    # make sure to do strict saninity checks on the in bound paramaters.
    pass
    
  def to_contractor( self ):
    # this is sent to the contractor, first paramater is the plugin in contractor, the second is the function inside the plugin to call, third is the value to send to the function
    # this is only called once, after execute is called and ready is called ( and returns False )
    # return ( 'builtin', 'nop', None )
    # if None is returned, contractor will not be notified to do anything
    return None
    
  def from_contractor( self, paramaters ):
    # return value is send back to contractor so the plugin in contractor can get some feedback
    # can be called multiple times, depending on what the plugin is coded to do
    return True

class Runner( object ):
  ok now do it!!!
