from contractor.tscript.runner import ExternalFunction, ParamaterError


class setPXE( ExternalFunction ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )

  @property
  def ready( self ):
    return True

  def setup( self, parms ):
    try:
      pxe = parms[ 'pxe' ]
    except KeyError:
      raise ParamaterError( 'pxe', 'required' )

    try:
      interface = parms[ 'interface' ]
    except KeyError:
      raise ParamaterError( 'interface', 'required' )

    interface.pxe = pxe
    interface.full_clean()
    interface.save()

# plugin exports

TSCRIPT_NAME = 'dhcp'

TSCRIPT_FUNCTIONS = {
                      'set_pxe': setPXE,
                    }

TSCRIPT_VALUES = {
                 }
