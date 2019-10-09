from contractor.tscript.runner import ExternalFunction, ParamaterError


class Constant( ExternalFunction ):
  @property
  def value( self ):
    return 42


class Multiply( ExternalFunction ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self._value = 0

  def setup( self, parms ):
    try:
       self._value = int( parms[ 'value' ] )
    except ( KeyError, ValueError ):
      raise ParamaterError( 'value', 'not provided or is not an int' )

  @property
  def value( self ):
    return self._value * 10

  def __getstate__( self ):
    return self._value

  def __setstate__( self, state ):
    self._value = state


class Remote( ExternalFunction ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.state = None
    self.counter = 0

  @property
  def done( self ):
    return self.state is not None

  @property
  def message( self  ):
    if self.state is None:
      return 'Not Initilized'

    else:
      return 'Current State "{0}"'.format( self.state )

  @property
  def value( self ):
    if self.state == 'Bad':
      return Exception( 'Bad things happened' )

    return self.state

  def run( self ):
    self.counter += 1

  def toSubcontractor( self ):
    return ( 'remote_func', 'the count "{0}"'.format( self.counter ) )

  def fromSubcontractor( self, data ):
    self.state = data

  def setup( self, parms ):
    self.counter = 0

  def __getstate__( self ):
    return ( self.state, self.counter )

  def __setstate__( self, state ):
    self.state = state[0]
    self.counter = state[1]


class Count( ExternalFunction ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.counter = 0
    self.count_by = 0
    self.stop_at = 0

  def setup( self, parms ):
    try:
       self.count_by = int( parms[ 'count_by' ] )
    except ( KeyError, ValueError ):
      raise ParamaterError( 'count_by', 'not provided or is not an int' )

    try:
       self.stop_at = int( parms[ 'stop_at' ] )
    except ( KeyError, ValueError ):
      raise ParamaterError( 'stop_at', 'not provided or is not an int' )

  def run( self ):
    self.counter += self.count_by

  @property
  def done( self ):
    return self.counter >= self.stop_at

  @property
  def message( self ):
    return 'at {0} of {1}'.format( self.counter, self.stop_at )

  def __getstate__( self ):
    return ( self.counter, self.count_by, self.stop_at )

  def __setstate__( self, state ):
    self.counter = state[0]
    self.count_by = state[1]
    self.stop_at = state[2]


big_stuff = 'the big stuff'
little_stuff = None
other_stuff = None


def get_bigstuff():
  return big_stuff


def set_littlestuff( value ):
  global little_stuff
  little_stuff = value


def get_otherstuff():
  return other_stuff


def set_otherstuff( value ):
  global other_stuff
  other_stuff = value

# plugin exports

TSCRIPT_NAME = 'testing'

TSCRIPT_FUNCTIONS = {
                      'constant': Constant,
                      'multiply': Multiply,
                      'remote': Remote,
                      'count': Count
                    }

TSCRIPT_VALUES = {
                   'bigstuff': ( get_bigstuff, None ),
                   'littlestuff': ( None, set_littlestuff ),
                   'otherstuff': ( get_otherstuff, set_otherstuff )
                 }
