import pytest

from django.core.exceptions import ValidationError

from contractor.Site.models import Site
from contractor.BluePrint.models import StructureBluePrint, FoundationBluePrint
from contractor.Building.models import Foundation, Structure
from contractor.Survey.models import Plot
from contractor.lib.config import getConfig
from contractor.plugins.LibVirt.models import LibVirtFoundation, LibVirtComplex, _vmSpec
from contractor.plugins.IPMI.models import IPMIFoundation
from contractor.plugins.RedFish.models import RedFishFoundation


def _base( name, foundation_type='Unknown' ):
  s1 = Site( name='{0}site'.format( name ), description='site' )
  s1.config_values = {}
  s1.full_clean()
  s1.save()

  fb1 = FoundationBluePrint( name='{0}fdnb'.format( name ), description='fdn bp' )
  fb1.foundation_type_list = [ foundation_type ]
  fb1.full_clean()
  fb1.save()

  sb1 = StructureBluePrint( name='{0}strb'.format( name ), description='str bp' )
  sb1.full_clean()
  sb1.save()
  sb1.foundation_blueprint_list.add( fb1 )

  return s1, fb1, sb1


def _attach( s1, sb1, foundation, name ):
  st1 = Structure( site=s1, blueprint=sb1, hostname='{0}host'.format( name ), foundation=foundation )
  st1.config_values = {}
  st1.full_clean()
  st1.save()
  return st1


@pytest.mark.django_db()
def test_base_is_plain_console():
  s1, fb1, sb1 = _base( 'a' )

  f1 = Foundation( site=s1, locator='afdn', blueprint=fb1 )
  f1.full_clean()
  f1.save()
  st1 = _attach( s1, sb1, f1, 'a' )

  assert f1.console == 'console'
  assert getConfig( st1 )[ '_console' ] == 'console'
  assert getConfig( f1 )[ '_console' ] == 'console'

  # the old generic override key is gone, it must have no effect
  st1.config_values = { 'console_port': 'ttyS2' }
  st1.full_clean()
  st1.save()
  s1.config_values = { 'console_port': 'ttyS3' }
  s1.full_clean()
  s1.save()
  assert getConfig( st1 )[ '_console' ] == 'console'


@pytest.mark.django_db()
def test_ipmi_uses_field():
  s1, fb1, sb1 = _base( 'b', 'IPMI' )

  plot = Plot( name='bplot', corners='here' )
  plot.full_clean()
  plot.save()

  f1 = IPMIFoundation( site=s1, locator='bfdn', blueprint=fb1, plot=plot,
                       ipmi_username='u', ipmi_password='p', ipmi_ip_address='10.0.0.5',
                       ipmi_sol_port='ttyS1' )
  f1.full_clean()
  f1.save()
  st1 = _attach( s1, sb1, f1, 'b' )

  assert f1.console == 'ttyS1'
  assert getConfig( st1 )[ '_console' ] == 'ttyS1'

  f1.ipmi_sol_port = 'console'
  f1.full_clean()
  f1.save()
  assert getConfig( st1 )[ '_console' ] == 'console'


@pytest.mark.django_db()
def test_redfish_uses_field():
  s1, fb1, sb1 = _base( 'c', 'RedFish' )

  plot = Plot( name='cplot', corners='here' )
  plot.full_clean()
  plot.save()

  f1 = RedFishFoundation( site=s1, locator='cfdn', blueprint=fb1, plot=plot,
                          redfish_username='u', redfish_password='p', redfish_ip_address='10.0.0.6',
                          redfish_sol_port='ttyS2' )
  f1.full_clean()
  f1.save()
  st1 = _attach( s1, sb1, f1, 'c' )

  assert f1.console == 'ttyS2'
  assert getConfig( st1 )[ '_console' ] == 'ttyS2'


@pytest.mark.django_db()
def test_libvirt_uses_field():
  s1, fb1, sb1 = _base( 'd', 'LibVirt' )

  # a complex needs a member structure, build a plain one first
  hostfb = FoundationBluePrint( name='dhostfdnb', description='host fdn bp' )
  hostfb.foundation_type_list = [ 'Unknown' ]
  hostfb.full_clean()
  hostfb.save()

  hostsb = StructureBluePrint( name='dhoststrb', description='host str bp' )
  hostsb.full_clean()
  hostsb.save()
  hostsb.foundation_blueprint_list.add( hostfb )

  hostf = Foundation( site=s1, locator='dhostfdn', blueprint=hostfb )
  hostf.full_clean()
  hostf.save()

  hoststr = Structure( site=s1, blueprint=hostsb, hostname='dhypervisor', foundation=hostf )
  hoststr.config_values = {}
  hoststr.full_clean()
  hoststr.save()

  cx = LibVirtComplex( site=s1, name='dcx', description='libvirt complex' )
  cx.full_clean()
  cx.save()
  cx.members.add( hoststr )

  f1 = LibVirtFoundation( site=s1, locator='dfdn', blueprint=fb1, libvirt_complex=cx )
  f1.full_clean()
  f1.save()

  # the field defaults to serial, and no structure is attached yet
  assert f1.structure is None
  assert f1.libvirt_console_type == 'serial'
  assert f1.console == 'ttyS0'
  assert getConfig( f1 )[ '_console' ] == 'ttyS0'

  st1 = _attach( s1, sb1, f1, 'd' )
  assert getConfig( st1 )[ '_console' ] == 'ttyS0'

  f1.libvirt_console_type = 'spice'
  f1.full_clean()
  f1.save()
  assert f1.console == 'console'
  assert getConfig( st1 )[ '_console' ] == 'console'

  f1.libvirt_console_type = 'serial'
  f1.full_clean()
  f1.save()
  assert getConfig( st1 )[ '_console' ] == 'ttyS0'

  # the field is the only source, a config value of the same name does not influence it
  st1.config_values = { 'libvirt_console_type': 'spice' }
  st1.full_clean()
  st1.save()
  s1.config_values = { 'libvirt_console_type': 'spice' }
  s1.full_clean()
  s1.save()
  assert getConfig( st1 )[ '_console' ] == 'ttyS0'

  # and the field is validated
  f1.libvirt_console_type = 'whatever'
  with pytest.raises( ValidationError ):
    f1.full_clean()


@pytest.mark.django_db()
def test_libvirt_vmspec_uses_field():
  s1, fb1, sb1 = _base( 'e', 'LibVirt' )

  hostfb = FoundationBluePrint( name='ehostfdnb', description='host fdn bp' )
  hostfb.foundation_type_list = [ 'Unknown' ]
  hostfb.full_clean()
  hostfb.save()

  hostsb = StructureBluePrint( name='ehoststrb', description='host str bp' )
  hostsb.full_clean()
  hostsb.save()
  hostsb.foundation_blueprint_list.add( hostfb )

  hostf = Foundation( site=s1, locator='ehostfdn', blueprint=hostfb )
  hostf.full_clean()
  hostf.save()

  hoststr = Structure( site=s1, blueprint=hostsb, hostname='ehypervisor', foundation=hostf )
  hoststr.config_values = {}
  hoststr.full_clean()
  hoststr.save()

  cx = LibVirtComplex( site=s1, name='ecx', description='libvirt complex' )
  cx.full_clean()
  cx.save()
  cx.members.add( hoststr )

  f1 = LibVirtFoundation( site=s1, locator='efdn', blueprint=fb1, libvirt_complex=cx )
  f1.full_clean()
  f1.save()

  st1 = _attach( s1, sb1, f1, 'e' )
  # a config value of the same name must not leak into the spec, the field is the only source
  st1.config_values = { 'libvirt_console_type': 'spice' }
  st1.full_clean()
  st1.save()

  assert _vmSpec( f1 )[ 'console_type' ] == 'serial'
  # ...and it agrees with what _console says, which is the whole point of using one field
  assert getConfig( st1 )[ '_console' ] == 'ttyS0'

  f1.libvirt_console_type = 'spice'
  f1.full_clean()
  f1.save()
  assert _vmSpec( f1 )[ 'console_type' ] == 'spice'
  assert getConfig( st1 )[ '_console' ] == 'console'


def test_create_carries_console_type():
  # the value has to survive from vm_spec into vm_parameters, that dict is what subcontractor
  # reads as vm_parameters.get( 'console_type', ... )
  from contractor.plugins.LibVirt.module import create
  from contractor.tscript.runner import ParameterError

  def _setup( vm_spec ):
    item = create()
    item.getScriptValue = lambda _, name: { 'foundation': _StubFoundation(),
                                            'libvirt_complex': _StubComplex(),
                                            'locator': 'testvm' }[ name ]
    item.setup( { 'vm_spec': vm_spec } )
    return item.vm_parameters

  base = { 'cpu_count': 1, 'memory_size': 512 }

  assert _setup( dict( base, console_type='serial' ) )[ 'console_type' ] == 'serial'
  assert _setup( dict( base, console_type='spice' ) )[ 'console_type' ] == 'spice'

  # missing falls back to the same default as the model field, rather than raising KeyError
  assert _setup( base )[ 'console_type' ] == 'serial'

  # and a bad value is a ParameterError, not a KeyError
  with pytest.raises( ParameterError ):
    _setup( dict( base, console_type='whatever' ) )


class _StubFoundation():
  # create.setup only uses the foundation for it's interface list
  class _Ifaces():
    def all( self ):
      return self

    def order_by( self, _ ):
      return []

  networkinterface_set = _Ifaces()


class _StubComplex():
  connection_parameters = { 'host': '127.0.0.1' }
