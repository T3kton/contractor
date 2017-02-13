from contractor.Site.models import Site
from contractor.BluePrint.models import BluePrint
from contractor.Building.models import Foundation, Structure

def _siteConfig( site ):
  result = {
             'domain_name': None,
             'domain_search': [],
             'dns_servers': [],
             'log_servers': []
            }

  return result

def _bluePrintConfig( blueprint ):
  return {}

def _foundationConfig( foundation ):
  return {}

def _structureConfig( structure ):
  result = {
             'hostname': structure.hostname
            }

  return result

def getConfig( target ): # combine depth first the config values
  result = {}

  if isinstance( target, Site ):
    result.update( _siteConfig( target ) )

  elif isinstance( target, BluePrint ):
    result.update( _siteConfig( target.site ) )
    result.update( _bluePrintConfig( target ) )

  elif isinstance( target, Foundation ):
    result.update( _siteConfig( target.blueprint.site ) )
    result.update( _bluePrintConfig( target.blueprint ) )
    result.update( _foundationConfig( target ) )

  elif isinstance( target, Structure ):
    result.update( _siteConfig( target.blueprint.site ) )
    result.update( _bluePrintConfig( target.blueprint ) )
    result.update( _foundationConfig( target.foundation ) )
    result.update( _structureConfig( target ) )

  return result
