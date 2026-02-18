import re

#
# create a map of items to match
#  each item should have a "name"/"path" in the id map (regex?) (stored as the key(name))
#  should match attributes (regex)
#  min/max count
#
# the template should match exactly
# can have a wild card name as a catch all
#


def validateTemplate( id_map, validation_template ):  # return message as a string if something does not match
  for name, pattern in validation_template.items():
    try:
      value = id_map[ name.split( '.' ) ]
    except KeyError:
      return 'Item "{0}" not found'.format( name )

    if not re.match( pattern, value ):
      return 'Item "{0}" does not match "{1}"'.format( name, id_map[ name ] )

  return None
