from cinp.orm_django import DjangoCInP as CInP

from contractor.Site.models import Site
from contractor.Utilities.models import AddressBlock
from contractor.Foreman.lib import processJobs, jobResults, jobError
from contractor.lib.config import getConfig

cinp = CInP( 'SubContractor', '0.1' )


# these are only for subcontractor to talk to, thus some of the job_id short cuts
@cinp.staticModel()  # TODO: move to  Foreman?
class Dispatch():
  def __init__( self ):
    super().__init__()

  @cinp.action( return_type={ 'type': 'Map', 'is_array': True }, paramater_type_list=[ { 'type': 'Model', 'model': Site }, { 'type': 'String', 'is_array': True }, 'Integer' ] )
  @staticmethod
  def getJobs( site, module_list, max_jobs=10 ):
    result = processJobs( site, module_list, max_jobs )
    return result

  @cinp.action( return_type='String', paramater_type_list=[ 'Integer', 'String', 'Map' ] )
  @staticmethod
  def jobResults( job_id, cookie, data ):
    return jobResults( job_id, cookie, data )

  @cinp.action( paramater_type_list=[ 'Integer', 'String', 'String' ] )
  @staticmethod
  def jobError( job_id, cookie, msg ):
    jobError( job_id, cookie, msg )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True


@cinp.staticModel()
class DHCPd():
  def __init__( self ):
    super().__init__()

  @cinp.action( return_type={ 'type': 'Map', 'is_array': True }, paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def getDynamicPools( site ):
    result = []
    site_config = getConfig( site )
    try:
      dns_server = site_config[ 'dns_servers' ][0]
    except ( KeyError, IndexError ):
      dns_server = '1.1.1.1'

    domain_name = site_config[ 'domain_name' ]

    addr_block_list = AddressBlock.objects.filter( site=site, baseaddress__dynamicaddress__isnull=False ).distinct()  # without the distinct we get an AddressBlock for each DynamicAddress
    for addr_block in addr_block_list:
      item = {
               'address_map': {},
               'gateway': addr_block.gateway,
               'name': addr_block.pk,
               'netmask': addr_block.netmask,
               'dns_server': dns_server,
               'domain_name': domain_name
              }

      for addr in addr_block.baseaddress_set.filter( dynamicaddress__isnull=False ):
        addr = addr.subclass
        try:  # TODO: this needs to be retought a bit, really should be passing in the bootfile
          addr.pxe.name
          item[ 'address_map' ][ addr.ip_address ] = 'undionly_console.kpxe'
        except AttributeError:
          item[ 'address_map' ][ addr.ip_address ] = None

      result.append( item )

    return result

  @cinp.action( return_type={ 'type': 'Map' }, paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def getStaticPools( site ):
    result = {}
    addr_block_list = AddressBlock.objects.filter( site=site, baseaddress__address__networked__isnull=False )
    for addr_block in addr_block_list:
      for addr in addr_block.baseaddress_set.filter( address__networked__isnull=False ):
        addr = addr.subclass
        iface = addr.interface
        if iface is None or iface.mac is None:
          continue

        result[ iface.mac ] = {
                                'ip_address': addr.ip_address,
                                'netmask': addr_block.netmask,
                                'gateway': addr_block.gateway,
                                'host_name': addr.structure.hostname,
                                'boot_file': 'undionly_console.kpxe'
                              }

        site_config = addr_block.site.getConfig()

        try:
          result[ iface.mac ][ 'dns_server' ] = site_config[ 'dns_servers' ][0]
        except ( KeyError, IndexError ):
          pass

        try:
          result[ iface.mac ][ 'domain_name' ] = site_config[ 'domain_name' ]
        except KeyError:
          pass

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True
