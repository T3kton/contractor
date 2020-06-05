from cinp.orm_django import DjangoCInP as CInP

from contractor.Site.models import Site
from contractor.Utilities.models import AddressBlock, NetworkAddressBlock
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
    if verb == 'DESCRIBE':
      return True

    return verb == 'CALL' and user.username == 'subcontractor'


@cinp.staticModel()  # TODO: static poller
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

    domain_name = site_config.get( 'domain_name', '' )

    # without the distinct we get an AddressBlock for each DynamicAddress
    for address_block in AddressBlock.objects.filter( site=site, baseaddress__dynamicaddress__isnull=False ).distinct():
      item = {
               'gateway': address_block.gateway,
               'name': address_block.pk,
               'netmask': address_block.netmask,
               'dns_server': dns_server,
               'domain_name': domain_name
              }

      item[ 'address_list' ] = [ addr.ip_address for addr in address_block.baseaddress_set.filter( dynamicaddress__isnull=False ) ]

      result.append( item )

    return result

  @cinp.action( return_type={ 'type': 'Map' }, paramater_type_list=[ { 'type': 'Model', 'model': Site } ] )
  @staticmethod
  def getStaticPools( site ):
    result = {}
    # without the distinct we get an AddressBlock for each Networked
    for address_block in AddressBlock.objects.filter( site=site, baseaddress__address__networked__isnull=False ).distinct():
      for addr in address_block.baseaddress_set.filter( address__networked__isnull=False ):
        addr = addr.subclass
        iface = addr.interface
        if iface is None or iface.mac is None:
          continue

        try:
          nab = address_block.networkaddressblock_set.get( network=iface.network )
        except NetworkAddressBlock.DoesNotExist:
          continue

        result[ iface.mac ] = {
                                'ip_address': addr.ip_address,
                                'netmask': address_block.netmask,
                                'gateway': address_block.gateway,
                                'host_name': addr.structure.hostname,
                                'config_uuid': addr.structure.config_uuid,
                                'mtu': iface.network.mtu,
                                'vlan': nab.vlan,
                                'console': addr.console
                              }

        site_config = address_block.site.getConfig()

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
    if verb == 'DESCRIBE':
      return True

    return verb == 'CALL' and user.username == 'subcontractor'
