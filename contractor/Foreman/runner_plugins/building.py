from contractor.lib.config import getConfig


def getWrapper( target, key ):  # TODO: find a way to make this less expensive, mabey something that can detect if the target has changed, without calling getConfig
  config = getConfig( target )
  return config[ key ]


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


class FoundationPlugin( object ):
  TSCRIPT_NAME = 'foundation'

  def __init__( self, foundation, write=True ):
    super().__init__()
    self._dirty_list = []
    if isinstance( foundation, tuple ):
      self.foundation_class = foundation[0]
      self.foundation_pk = foundation[1]
      self.foundation = self.foundation_class.objects.get( pk=self.foundation_pk )

    else:
      self.foundation = foundation.subclass
      self.foundation_class = self.foundation.__class__
      self.foundation_pk = self.foundation.pk

    self.write = write

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
  def __init__( self, foundation, _=None ):
    super().__init__( foundation, write=False )


class StructurePlugin( object ):  # ie: structure with some settable attributes, 'config' is structures (with the foundation merged in of course)
  TSCRIPT_NAME = 'structure'

  def __init__( self, structure ):
    super().__init__()
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
    result[ 'provisioning_ip' ] = ( lambda: self.structure.provisioning_ip, None )
    result[ 'provisioning_interface' ] = ( lambda: self.structure.provisioning_interface, None )

    return result

  def getFunctions( self ):
    result = {}

    return result

  def __reduce__( self ):
    return ( self.__class__, ( ( self.structure_class, self.structure_pk ), ) )


class ROStructurePlugin( StructurePlugin ):  # curently Structure is RO, this is so we don't have to figure out what should be RO later
  def __init__( self, structure ):
    super().__init__( structure )
