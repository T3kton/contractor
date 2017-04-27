from datetime import datetime, timezone

"""
  The Config Value Caculation Process

  config values are applied in layers, for all layers applicable to that target
the layers are in order from applied last to applied first (ie: the items listed
first are layerd over the ones under it)

 - Site
 - BluePrint
 - Foundation
 - Structure

For Site and BluePrint, the values of the parents are overlied by the children.

Foundation does not it's self have values, however attributes of the foundation,
and possible hardware configuratoin values would be applied.

config value names must compliy with the regex: ^[{}\-~]?([a-zA-Z0-9]+:)?[a-zA-Z0-9][a-zA-Z0-9_\-]*$

if the first charater is: (also processed in this order)
  - : remove from the value so far
  <nothing> : overlay/replace value so far with new value
  { : prepend to the value so far (same affect as append on dict/maps)
  } : append to the value so far
  ~ : mask/remove value so far, (NOTE: value is ignored)

if [a-zA-Z0-9]+: is present, the value key/value is only applied if the pre ':' matches the classes indicated by the foundation

"""


VALUE_SORT_ORDER = '-_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{}~'


def value_key( item ):
  return VALUE_SORT_ORDER.index( item[0] )


def _updateConfig( config_value_map, class_list, config ):
  for name in sorted( config_value_map.keys(), key=value_key ):
    try:
      ( class_type, name ) = name.split( ':' )
    except ValueError:
      class_type = None

    if class_type is not None and class_type not in class_list:
      continue

    value = config_value_map[ name ]

    if name[0] == '-':
      name = name[ 1: ]
      try:
        old_value = config[ name ]
      except KeyError:
        config[ name ] = value
        continue

      config[ name ] = old_value - value

    elif name[0] == '{':
      name = name[ 1: ]
      try:
        old_value = config[ name ]
      except KeyError:
        config[ name ] = value
        continue

      config[ name ] = value + old_value

    elif name[0] == '}':
      name = name[ 1: ]
      try:
        old_value = config[ name ]
      except KeyError:
        config[ name ] = value
        continue

      config[ name ] = old_value + value

    elif name == '~':
      name = name[ 1: ]
      try:
        del config[ name ]
      except KeyError:
        pass

    else:
      config[ name ] = value


def _siteConfigInternal( site, class_list, config ):
  lastModified = site.updated

  if site.parent is not None:
    lastModified = max( lastModified, _siteConfigInternal( site.parent, class_list, config ) )

  _updateConfig( site.config_values, class_list, config )

  return lastModified


def _siteConfig( site, class_list, config ):
  config[ 'domain_name' ] = None
  config[ 'domain_search' ] = []  # TODO: need to make sure these are lists, have to have clean on Site.save do that
  config[ 'dns_servers' ] = []
  config[ 'log_servers' ] = []

  lastModified = _siteConfigInternal( site, class_list, config )

  config[ 'site' ] = site.pk

  return lastModified


def _bluePrintConfigInternal( blueprint, class_list, config ):
  lastModified = blueprint.updated

  if blueprint.parent is not None:
    lastModified = max( lastModified, _bluePrintConfigInternal( blueprint.parent, class_list, config ) )

  _updateConfig( blueprint.config_values, class_list, config )
  return lastModified


def _bluePrintConfig( blueprint, class_list, config ):
  lastModified = _bluePrintConfigInternal( blueprint, class_list, config )

  config[ 'blueprint' ] = blueprint.pk

  return lastModified


def _foundationConfig( foundation, class_list, config ):
  _updateConfig( foundation.config_values, class_list, config )

  config.update( foundation.configValues() )
  return foundation.updated


def _structureConfig( structure, class_list, config ):
  _updateConfig( structure.config_values, class_list, config )

  config.update( structure.configValues() )
  return structure.updated


def getConfig( target ):  # combine depth first the config values
  config = {}
  lastModified = datetime( 1, 1, 1, tzinfo=timezone.utc )

  if hasattr( target, 'class_list' ):
    class_list = target.class_list
  elif hasattr( target, 'foundation' ):
    class_list = target.foundation.class_list
  else:
    class_list = []

  if target.__class__.__name__ == 'Site':
    lastModified = max( lastModified, _siteConfig( target, class_list, config ) )

  elif target.__class__.__name__ in ( 'BluePrint', 'StructureBluePrint', 'FoundationBluePrint' ):
    lastModified = max( lastModified, _bluePrintConfig( target, class_list, config ) )

  elif target.__class__.__name__ == 'Structure':
    lastModified = max( lastModified, _siteConfig( target.site, class_list, config ) )
    lastModified = max( lastModified, _bluePrintConfig( target.blueprint, class_list, config ) )
    lastModified = max( lastModified, _foundationConfig( target.foundation, class_list, config ) )
    lastModified = max( lastModified, _structureConfig( target, class_list, config ) )

  elif hasattr( target, 'blueprint' ):  # foundations should end up here, can't count on the class name, that will depend on which foundation type is being used
    lastModified = max( lastModified, _siteConfig( target.site, class_list, config ) )
    lastModified = max( lastModified, _bluePrintConfig( target.blueprint, class_list, config ) )
    lastModified = max( lastModified, _foundationConfig( target, class_list, config ) )

  else:
    raise ValueError( 'Don\'t know how to get config for "{0}"'.format( target ) )

  config[ '_last_modified' ] = lastModified
  config[ '_contractor_host' ] = 'http://127.0.0.1/'
  return config
