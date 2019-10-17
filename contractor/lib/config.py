import copy
import json
from datetime import datetime, timezone
from jinja2 import Environment, Undefined, TemplateSyntaxError

from django.conf import settings

from contractor.fields import config_name_regex

VALUE_SORT_ORDER = '-_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz<>~'
_jinja_environment = None


def value_key( item ):
  return VALUE_SORT_ORDER.index( item[0] )


def JSONDefault( obj ):
  if isinstance( obj, datetime ):
    return obj.isoformat()

  if isinstance( obj, Undefined ):
    return ''

  return json.JSONEncoder.default( obj )


def _jinjaEnv():
  global _jinja_environment

  if _jinja_environment is not None:
    return _jinja_environment

  _jinja_environment = Environment()
  _jinja_environment.policies[ 'json.dumps_kwargs' ] = { 'sort_keys': True, 'default': JSONDefault }

  return _jinja_environment


def _updateConfig( config_value_map, class_list, config ):
  if config_value_map is None:
    return

  for name in sorted( config_value_map.keys(), key=value_key ):
    if not config_name_regex.match( name ):
      raise ValueError( 'invalid config value name "{0}"'.format( name ) )

    value = config_value_map[ name ]

    try:
      ( name, class_type ) = name.split( ':' )
    except ValueError:
      class_type = None

    if class_type is not None and class_type not in class_list:
      continue

    if name[0] in '-<>':
      op = name[0]
      name = name[ 1: ]
      try:
        old_value = config[ name ]
      except KeyError:
        if op != '-':
          config[ name ] = value
        continue

      if isinstance( old_value, str ):
        if not isinstance( value, str ):
          value = str( value )

        if op == '-':
          config[ name ] = old_value.replace( value, '', 1 )

        elif op == '<':
          config[ name ] = value + old_value

        elif op == '>':
          config[ name ] = old_value + value

      elif isinstance( old_value, dict ):
        if op == '-':
          if isinstance( value, str ):
            try:
              del config[ name ][ value ]
            except KeyError:
              pass

          elif isinstance( value, list ):
            for key in value:
              try:
                del config[ name ][ key ]
              except KeyError:
                pass

        else:
          if not isinstance( value, dict ):
            raise ValueError( 'can only append/prepend dict with a dict' )

          config[ name ].update( value )

      elif isinstance( old_value, list ):
        if isinstance( value, list ):
          if op == '-':
            config[ name ] = old_value
            for item in value:
              try:
                config[ name ].remove( item )
              except ValueError:
                pass

          elif op == '<':
            config[ name ] = value + old_value

          elif op == '>':
            config[ name ] = old_value + value

        else:
          if op == '-':
            config[ name ] = old_value
            try:
              config[ name ].remove( value )
            except ValueError:
              pass

          elif op == '<':
            config[ name ] = [ value ] + old_value

          elif op == '>':
            config[ name ] = old_value + [  value ]

    elif name[0] == '~':
      name = name[ 1: ]
      try:
        del config[ name ]
      except KeyError:
        pass

    else:
      config[ name ] = value


def _siteConfigInternal( site, class_list, config ):
  last_modified = site.updated

  if site.parent is not None:
    last_modified = max( last_modified, _siteConfigInternal( site.parent, class_list, config ) )

  _updateConfig( site.config_values, class_list, config )

  return last_modified


def _siteConfig( site, class_list, config ):
  last_modified = _siteConfigInternal( site, class_list, config )

  config[ '_site' ] = site.pk

  return last_modified


def _bluePrintConfigInternal( blueprint, class_list, config ):
  last_modified = blueprint.updated

  for parent in blueprint.parent_list.all():
    last_modified = max( last_modified, _bluePrintConfigInternal( parent, class_list, config ) )

  _updateConfig( blueprint.config_values, class_list, config )
  return last_modified


def _bluePrintConfig( blueprint, class_list, config ):
  last_modified = _bluePrintConfigInternal( blueprint, class_list, config )

  config[ '_blueprint' ] = blueprint.pk

  return last_modified


def _foundationConfig( foundation, class_list, config ):
  config.update( foundation.configAttributes() )
  complex = getattr( foundation, 'complex', None )
  if foundation.complex is not None:
    config.update( complex.configAttributes() )
    return max( foundation.updated, complex.updated )

  return foundation.updated


def _structureConfig( structure, class_list, config ):
  _updateConfig( structure.config_values, class_list, config )

  config.update( structure.configAttributes() )
  return structure.updated


def getConfig( target ):
  config = {}
  last_modified = datetime( 1, 1, 1, tzinfo=timezone.utc )

  if hasattr( target, 'class_list' ):
    class_list = target.class_list

  elif hasattr( target, 'foundation' ):
    class_list = target.foundation.subclass.class_list

  else:
    class_list = []

  if target.__class__.__name__ == 'Site':
    last_modified = max( last_modified, _siteConfig( target, class_list, config ) )

  elif target.__class__.__name__ in ( 'BluePrint', 'StructureBluePrint', 'FoundationBluePrint' ):
    last_modified = max( last_modified, _bluePrintConfig( target, class_list, config ) )

  elif target.__class__.__name__ == 'Structure':
    last_modified = max( last_modified, _bluePrintConfig( target.blueprint, class_list, config ) )
    last_modified = max( last_modified, _siteConfig( target.site, class_list, config ) )
    last_modified = max( last_modified, _foundationConfig( target.foundation.subclass, class_list, config ) )
    last_modified = max( last_modified, _structureConfig( target, class_list, config ) )

  elif 'Foundation' in [ i.__name__ for i in target.__class__.__mro__ ]:
    last_modified = max( last_modified, _bluePrintConfig( target.blueprint, class_list, config ) )
    last_modified = max( last_modified, _siteConfig( target.site, class_list, config ) )
    last_modified = max( last_modified, _foundationConfig( target, class_list, config ) )
    try:
      config[ '_structure_id' ] = target.structure.pk
    except AttributeError:
      pass

  elif 'BaseAddress' in [ i.__name__ for i in target.__class__.__mro__ ]:
    last_modified = max( last_modified, _siteConfig( target.address_block.site, class_list, config ) )

  else:
    raise ValueError( 'Don\'t know how to get config for "{0}"'.format( target ) )

  # Global Attributes
  config[ '__last_modified' ] = last_modified
  config[ '__timestamp' ] = datetime.now( timezone.utc )
  config[ '__contractor_host' ] = settings.CONTRACTOR_HOST
  try:
    config[ '__pxe_template_location' ] = '{0}config/pxe_template/c/{1}'.format( settings.CONTRACTOR_HOST, config[ '_structure_config_uuid' ] )
  except KeyError:
    config[ '__pxe_template_location' ] = '{0}config/pxe_template/'.format( settings.CONTRACTOR_HOST )
  config[ '__pxe_location' ] = settings.PXE_IMAGE_LOCATION

  return config


def _merge( target, value_map ):
  if isinstance( target, dict ):
    dirty = False
    new = {}
    for key in target.keys():
      new[ key ], tmp = _merge( target[ key ], value_map )
      dirty |= tmp

    return new, dirty

  if isinstance( target, list ):
    dirty = False
    new = []
    for i in range( 0, len( target ) ):
      val, tmp = _merge( target[ i ], value_map )
      new.append( val )
      dirty |= tmp

    return new, dirty

  if isinstance( target, str ):
    new = _jinjaEnv().from_string( target ).render( **value_map )
    return new, new != target

  return target, False


def mergeValues( value_map ):
  result = copy.deepcopy( value_map )

  dirty = True
  while dirty:  # going to try and do this breath first, however we don't have a predictable order, not going to promise much
    result, dirty = _merge( result, result )

  return result


def renderTemplate( template, value_map ):
  env = _jinjaEnv()

  value_map = mergeValues( value_map )  # merge first, this way results are more consistant with requests that are getting just the values

  try:
    while template.count( '{{' ):
      tpl = env.from_string( template )
      template = tpl.render( **value_map )

  except TemplateSyntaxError as e:
    raise Exception( 'Error parsing template: "{0}" on line: "{1}"'.format( e.message, e.lineno ) )

  return template
