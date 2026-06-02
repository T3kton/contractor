from contractor.BluePrint.models import PXE
from contractor.tscript.runner import ExternalFunction, ParameterError


class setPXE( ExternalFunction ):
  def __init__( self, *args, **kwargs ):
    super().__init__( *args, **kwargs )

  @property
  def ready( self ):
    return True

  def setup( self, parms ):
    try:
      pxe_name = parms[ 'pxe' ]
    except KeyError:
      raise ParameterError( 'pxe', 'required' )

    try:
      interface = parms[ 'interface' ]
    except KeyError:
      raise ParameterError( 'interface', 'required' )

    if interface is None:
      raise ParameterError( 'interface', 'can not be None' )

    try:
      pxe = PXE.objects.get( name=pxe_name )
    except PXE.DoesNotExist:
      raise ParameterError( 'pxe', 'pxe "{0}" not found'.format( pxe_name ) )

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
