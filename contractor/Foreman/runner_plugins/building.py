from contractor.fields import config_name_regex
from contractor.lib.config import getConfig
from contractor.tscript.runner import ParamaterError, Interrupt


def getWrapper( target, key ):  # TODO: find a way to make this less expensive, mabey something that can detect if the target has changed, without calling getConfig
  config = getConfig( target )
  return config[ key ]


class SetConfig( object ):
  def __init__( self, structure, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.structure = structure

  def __call__( self, name, value ):
    path = [ int( i ) if i.isdigit() else i for i in name.split( '.' ) ]
    name = path.pop( 0 )

    if not config_name_regex.match( name ):
      raise ParamaterError( 'name', 'invalid' )

    config_values = self.structure.config_values

    if name not in config_values:
      raise ParamaterError( 'name', '"{0}" not found'.format( name ) )

    while path:
      if not isinstance( config_values, ( dict, list ) ):
        raise ParamaterError( 'name', '"{0}" at non indexable level'.format( name ) )

      try:
        config_values = config_values[ name ]
      except ( KeyError, IndexError ):
        raise ParamaterError( 'name', '"{0}" not found'.format( name ) )

      name = path.pop( 0 )

    if not isinstance( config_values, ( dict, list ) ):
      raise ParamaterError( 'name', '"{0}" at non indexable level'.format( name ) )

    if name not in config_values:
      raise ParamaterError( 'name', '"{0}" not found'.format( name ) )

    config_values[ name ] = value

    self.structure.full_clean()
    self.structure.save( update_fields=[ 'config_values' ] )


class ConfigPlugin( object ):
  TSCRIPT_NAME = 'config'

  def __init__( self, target ):
    super().__init__()
    if isinstance( target, tuple ):
      self.target_class = target[0]
      self.target_pk = target[1]
      self.target = self.target_class.objects.get( pk=self.target_pk )

    else:
      self.target = target.subclass
      self.target_class = self.target.__class__
      self.target_pk = self.target.pk

  def getValues( self ):
    config = getConfig( self.target )
    result = {}
    for key in config:
      result[ key ] = ( lambda key=key: getWrapper( self.target, key ), None )

    return result

  def getFunctions( self ):
    result = {}

    return result

  def __reduce__( self ):
    return ( self.__class__, ( ( self.target_class, self.target_pk ), ) )


class FoundationPlugin( object ):  # TODO: really should have the RO version be the base class?
  TSCRIPT_NAME = 'foundation'

  def __init__( self, foundation, write=True ):
    super().__init__()
    self.write = write
    self._dirty_list = []
    if isinstance( foundation, tuple ):
      self.foundation_class = foundation[0]
      self.foundation_pk = foundation[1]
      self.foundation = self.foundation_class.objects.get( pk=self.foundation_pk )

    else:
      self.foundation = foundation.subclass
      self.foundation_class = self.foundation.__class__
      self.foundation_pk = self.foundation.pk

    self.value_map = self.foundation_class.getTscriptValues( write )
    self.function_map = self.foundation_class.getTscriptFunctions()

  def _setValue( self, name, val ):
    setter = self.value_map[ name ][1]
    setter( self.foundation, val )
    self._dirty_list.append( name )

  def getValues( self ):
    result = {}
    for key in self.value_map:
      getter = self.value_map[ key ][0]
      setter = self.value_map[ key ][1]
      if setter is not None and self.write:
        result[ key ] = ( lambda getter=getter: getter( self.foundation ), lambda val, name=key: self._setValue( name, val ) )
      else:
        result[ key ] = ( lambda getter=getter: getter( self.foundation ), None )

    result[ 'id' ] = ( lambda: self.foundation_pk, None )
    result[ 'class' ] = ( lambda: self.foundation_class, None )
    result[ 'foundation' ] = ( lambda: self.foundation, None )
    result[ 'provisioning_interface' ] = ( lambda: self.foundation.provisioning_interface, None )

    return result

  def getFunctions( self ):
    result = {}
    for key in self.function_map:
      builder = self.function_map[ key ]
      result[ key ] = lambda builder=builder: builder( self.foundation )

    return result

  def __reduce__( self ):
    if self.write and self._dirty_list:
      self.foundation.full_clean()
      self.foundation.save( update_fields=self._dirty_list )

    return ( self.__class__, ( ( self.foundation_class, self.foundation_pk ), self.write ) )


class ROFoundationPlugin( FoundationPlugin ):
  def __init__( self, foundation, write=None ):
    super().__init__( foundation, write=False )


class StructurePlugin( object ):  # ie: structure with some settable attributes, 'config' is structures (with the foundation merged in of course)
  TSCRIPT_NAME = 'structure'

  def __init__( self, structure, write=True ):
    super().__init__()
    self.write = write
    self._dirty_list = []
    if isinstance( structure, tuple ):
      self.structure_class = structure[0]
      self.structure_pk = structure[1]
      self.structure = self.structure_class.objects.get( pk=self.structure_pk )

    else:
      self.structure = structure
      self.structure_class = self.structure.__class__
      self.structure_pk = self.structure.pk

  def getValues( self ):
    result = {}

    result[ 'id' ] = ( lambda: self.structure.pk, None )
    result[ 'hostname' ] = ( lambda: self.structure.hostname, None )
    result[ 'provisioning_ip' ] = ( lambda: self.structure.provisioning_address.ip_address if self.structure.provisioning_address else None, None )
    result[ 'provisioning_interface' ] = ( lambda: self.structure.provisioning_interface, None )
    result[ 'primary_ip' ] = ( lambda: self.structure.primary_address.ip_address if self.structure.primary_address else None, None )
    result[ 'primary_interface' ] = ( lambda: self.structure.primary_interface, None )

    return result

  def getFunctions( self ):
    result = {}
    if self.write:
      result[ 'set_config' ] = lambda: SetConfig( self.structure )

    return result

  def __reduce__( self ):
    if self.write and self._dirty_list:
      self.structure.full_clean()
      self.structure.save( update_fields=self._dirty_list )

    return ( self.__class__, ( ( self.structure_class, self.structure_pk ), self.write ) )


class ROStructurePlugin( StructurePlugin ):
  def __init__( self, structure, write=None ):
    super().__init__( structure, write=False  )


class SignalingPlugin( object ):
  TSCRIPT_NAME = 'signaling'

  def __init__( self, target, job=None ):
    super().__init__()
    if isinstance( target, tuple ):
      self.cookie = target[0]
      self.complete = target[1]
      self.pxe_name = target[2]

    else:
      if job is None:
        raise ValueError( 'job is required' )

      # if target.__class__.__name__ == 'Structure':
      #   uuid = target.config_uuid
      # elif target.__class__.__name__ == 'Dependency':
      #   uuid = target.pk
      # else:
      #   uuid = target.locator

      self.cookie = '{0}'.format( job.pk )
      self.complete = False
      self.pxe_name = None

  def getValues( self ):
    result = {}

    result[ 'complete' ] = ( lambda: self.complete, None )

    return result

  def getFunctions( self ):
    result = {}

    result[ 'reset' ] = lambda: self.reset
    result[ 'wait_for_completion' ] = lambda: self.waitForCompletion

    return result

  def reset( self, pxe_name ):
    self.complete = False
    self.pxe_name = pxe_name

  def waitForCompletion( self ):
    if not self.complete:
      raise Interrupt( 'Not Complete' )

  def signal( self, cookie ):
    if cookie != '{0}({1})'.format( self.cookie, self.pxe_name ):
      return 'Invalid Cookie'

    self.complete = True
    return 'Recieved'

  def __reduce__( self ):
    return ( self.__class__, ( ( self.cookie, self.complete, self.pxe_name ), ) )
