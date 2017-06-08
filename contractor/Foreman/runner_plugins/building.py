from django.core.exceptions import ObjectDoesNotExist

from contractor.lib.config import getConfig


class ConfigPlugin( object ):  # this is purley Read Only, if wiring is needed have to set it to the structure/foundation's config_values, and figure out a way to reload
  TSCRIPT_NAME = 'config'

  def __init__( self, target ):
    super().__init__()
    if isinstance( target, dict ):
      self.config = target
    else:
      self.config = getConfig( target )

  def getValues( self ):
    result = {}
    for key in self.config:
      result[ key ] = ( lambda key=key: self.config[ key ], None )

    return result

  def getFunctions( self ):
    result = {}

    return result

  def __reduce__( self ):
    return ( self.__class__, ( self.config, ) )


class FoundationPlugin( object ):
  TSCRIPT_NAME = 'foundation'

  def __init__( self, foundation ):  # most of the time all that is needed is the locator, so we are going to cache that and only go get the object if other than locator is needed
    super().__init__()
    self._dirty_list = []
    if isinstance( foundation, tuple ):
      self._foundation = None
      self.foundation_class = foundation[0]
      self.foundation_pk = foundation[1]
      self.foundation_locator = foundation[2]

    else:
      self._foundation = foundation.subclass
      self.foundation_class = self._foundation.__class__
      self.foundation_pk = foundation.pk
      self.foundation_locator = foundation.locator

    self.value_map = self.foundation_class.getTscriptValues( True )
    self.function_map = self.foundation_class.getTscriptFunctions()

  @property
  def foundation( self ):
    if self._foundation is None:
      self._foundation = self.foundation_class.objects.get( pk=self.foundation_pk )

    return self._foundation

  def _setValue( self, name, val ):
    setter = self.value_map[ name ][1]
    setter( self.foundation, val )
    self._dirty_list.append( name )

  def getValues( self ):
    result = {}
    for key in self.value_map:
      getter = self.value_map[ key ][0]
      setter = self.value_map[ key ][1]
      if setter is not None:
        result[ key ] = ( lambda getter=getter: getter( self.foundation ), lambda val, name=key: self._setValue( name, val ) )
      else:
        result[ key ] = ( lambda getter=getter: getter( self.foundation ), None )

    result[ 'locator' ] = ( lambda: self.foundation_locator, None )

    return result

  def getFunctions( self ):
    result = {}
    for key in self.function_map:
      builder = self.function_map[ key ]
      result[ key ] = lambda builder=builder: builder( self.foundation )

    return result

  def __reduce__( self ):
    if self._foundation is not None and self._dirty_list:
      self._foundation.full_clean()
      self._foundation.save( update_fields=self._dirty_list )

    return ( self.__class__, ( ( self.foundation_class, self.foundation_pk, self.foundation_locator ), ) )


class StructureFoundationPlugin( FoundationPlugin ):  # ie: read only foundation
  def __init__( self, foundation ):
    super().__init__( foundation )
    # the same as Foundation plugin, except we want read only value_map, so replace value_map with this and call it good
    self.value_map = self.foundation_class.getTscriptValues( False )


class StructurePlugin( object ):  # ie: structure with some settable attributes, 'config' is structures (with the foundation merged in of course)
  TSCRIPT_NAME = 'structure'

  def __init__( self, structure ):
    super().__init__()
    self.structure = structure

  def getValues( self ):
    result = {}
    try:
      provisioning_ip = self.structure.address_set.get( is_provisioning=True )
    except ObjectDoesNotExist:
      provisioning_ip = None

    try:
      provisioning_interface = provisioning_ip.interface if provisioning_ip is not None else None
    except ObjectDoesNotExist:
      provisioning_interface = None

    result[ 'id' ] = ( lambda: self.structure.pk, None )
    result[ 'hostname' ] = ( lambda: self.structure.hostname, None )
    result[ 'provisioning_ip' ] = ( lambda: provisioning_ip.ip_address if provisioning_ip is not None else None, None )
    result[ 'provisioning_interface' ] = ( lambda: provisioning_interface if provisioning_interface is not None else None, None )

    return result

  def getFunctions( self ):
    result = {}

    return result
