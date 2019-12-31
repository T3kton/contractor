import re


def validateTemplate( id_map, template ):  # return message as a string if something does not match
  for name, pattern in template.items():
    try:
      value = id_map[ name.split( '.' ) ]
    except KeyError:
      return 'Item "{0}" not found'.format( name )

    if not re.match( pattern, value ):
      return 'Item "{0}" does not match "{1}"'.format( name, id_map[ name ] )

  return None
