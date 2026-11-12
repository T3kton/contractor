import pytest

from contractor.BluePrint.lib import validateTemplate, checkTemplate, TemplateError


def test_validate_template_empty():
  id_map = { 'hardware': {}, 'network': {}, 'disks': [] }

  # exact-match by default: an empty template means the id_map must have no keys either
  assert validateTemplate( id_map, {} ) == [ 'Unexpected item "disks"', 'Unexpected item "hardware"', 'Unexpected item "network"' ]
  assert validateTemplate( id_map, { '*': { '$any': True } } ) is None


def test_validate_template_literal_and_missing():
  id_map = { 'network': { 'eth0': { 'mac': 'aa:bb:cc:dd:ee:ff' } }, 'hardware': { 'vendor': 'Acme' } }

  assert validateTemplate( id_map, { 'network': { 'eth0': { 'mac': { '$match': '^[0-9a-f:]+$' } } }, 'hardware': { '$any': True } } ) is None
  assert validateTemplate( id_map, { 'hardware': { 'vendor': { '$match': '^Acme$' } }, 'network': { '$any': True } } ) is None

  assert validateTemplate( id_map, { 'network': { 'eth0': { 'mac': { '$match': '^ZZZ$' } } }, 'hardware': { '$any': True } } ) == [ 'Item "network.eth0.mac" value "aa:bb:cc:dd:ee:ff" does not match "^ZZZ$"' ]
  assert validateTemplate( id_map, { 'network': { 'eth1': { '$any': True } }, 'hardware': { '$any': True } } ) == [ 'Item "network.eth1" not found', 'Unexpected item "network.eth0"' ]
  assert validateTemplate( id_map, { 'bogus': { '$any': True } } ) == [ 'Item "bogus" not found', 'Unexpected item "hardware"', 'Unexpected item "network"' ]
  assert validateTemplate( id_map, { 'hardware': { 'vendor': { 'extra': { '$any': True } } }, 'network': { '$any': True } } ) == [ 'Item "hardware.vendor" is not an object' ]


def test_validate_template_exact_match_and_wildcard():
  id_map = { 'network': { 'eth0': { 'mac': 'aa:bb:cc:dd:ee:ff' }, 'eth1': { 'mac': '11:22:33:44:55:66' } } }

  # unnamed key with no wildcard is an error
  assert validateTemplate( id_map, { 'network': { 'eth0': { '$any': True } } } ) == [ 'Unexpected item "network.eth1"' ]

  # wildcard soaks up whatever isn't named explicitly
  assert validateTemplate( id_map, { 'network': { '*': { 'mac': { '$match': '^[0-9a-f:]+$' } } } } ) is None


def test_validate_template_optional_and_exists():
  id_map = { 'hardware': { 'vendor': 'Acme' } }

  assert validateTemplate( id_map, { 'hardware': { 'vendor': { '$any': True }, 'model': { '$optional': True, '$match': '.*' } } } ) is None
  assert validateTemplate( id_map, { 'hardware': { 'vendor': { '$any': True }, 'model': { '$match': '.*' } } } ) == [ 'Item "hardware.model" not found' ]
  assert validateTemplate( id_map, { 'hardware': { 'vendor': { '$exists': False }, '*': { '$any': True } } } ) == [ 'Item "hardware.vendor" is not allowed to be present' ]


def test_validate_template_optional_alone_is_any():
  # "$optional" with no other constraint means "I only care if it's there" -- if present, the
  # value can be anything (a scalar, a nonempty dict, ...), it is NOT required to be an empty dict
  id_map = { 'hardware': { 'total_ram': 137438953472, 'notes': { 'a': 1, 'b': 2 } } }

  template = { 'hardware': { 'total_ram': { '$optional': True }, 'notes': { '$optional': True }, '*': { '$any': True } } }
  assert validateTemplate( id_map, template ) is None

  # still enforces absence when missing is not allowed
  del id_map[ 'hardware' ][ 'notes' ]
  assert validateTemplate( id_map, { 'hardware': { 'notes': { '$match': '.*' }, '*': { '$any': True } } } ) == [ 'Item "hardware.notes" not found' ]

  # a bare {} (no reserved keys at all) still means "must be present and an empty dict"
  id_map[ 'hardware' ][ 'notes' ] = {}
  assert validateTemplate( id_map, { 'hardware': { 'notes': {}, '*': { '$any': True } } } ) is None
  id_map[ 'hardware' ][ 'notes' ] = { 'a': 1 }
  assert validateTemplate( id_map, { 'hardware': { 'notes': {}, '*': { '$any': True } } } ) == [ 'Unexpected item "hardware.notes.a"' ]


def test_validate_template_type():
  id_map = { 'hardware': { 'total_ram': 137438953472, 'total_cpu_count': 32, 'flag': True } }

  assert validateTemplate( id_map, { 'hardware': { '*': { '$any': True }, 'total_ram': { '$type': 'number' } } } ) is None
  assert validateTemplate( id_map, { 'hardware': { '*': { '$any': True }, 'flag': { '$type': 'bool' } } } ) is None
  assert validateTemplate( id_map, { 'hardware': { '*': { '$any': True }, 'total_ram': { '$type': 'str' } } } ) == [ 'Item "hardware.total_ram" is not of type "str"' ]
  # bool must not satisfy $type: number/int even though bool is an int subclass
  assert validateTemplate( id_map, { 'hardware': { '*': { '$any': True }, 'flag': { '$type': 'number' } } } ) == [ 'Item "hardware.flag" is not a number' ]


def test_validate_template_type_with_eq():
  # "$type" is checked before "$eq" and short-circuits -- combining them rejects a value that
  # "$eq" alone would accept via its numeric coercion (ex: the string "32" for an int 32)
  id_map = { 'hardware': { 'total_cpu_count': 32 } }

  assert validateTemplate( id_map, { 'hardware': { 'total_cpu_count': { '$type': 'int', '$eq': 32 } } } ) is None
  assert validateTemplate( id_map, { 'hardware': { 'total_cpu_count': { '$type': 'str', '$eq': '32' } } } ) == [ 'Item "hardware.total_cpu_count" is not of type "str"' ]

  id_map[ 'hardware' ][ 'total_cpu_count' ] = '32'
  assert validateTemplate( id_map, { 'hardware': { 'total_cpu_count': { '$eq': 32 } } } ) is None  # no "$type": coercion still applies
  assert validateTemplate( id_map, { 'hardware': { 'total_cpu_count': { '$type': 'int', '$eq': 32 } } } ) == [ 'Item "hardware.total_cpu_count" is not of type "int"' ]


def test_validate_template_min_max():
  id_map = { 'hardware': { 'total_ram': 137438953472, 'total_cpu_count': 8, 'bios_version': '2.10.3' } }
  template_base = { 'hardware': { '*': { '$any': True } } }

  def with_spec( name, spec ):
    template = { 'hardware': { '*': { '$any': True }, name: spec } }
    return template

  assert validateTemplate( id_map, with_spec( 'total_ram', { '$min': 34359738368 } ) ) is None
  assert validateTemplate( id_map, with_spec( 'total_cpu_count', { '$min': 16 } ) ) == [ 'Item "hardware.total_cpu_count" value "8" is less than "16"' ]
  assert validateTemplate( id_map, with_spec( 'bios_version', { '$min': '2.8.0' } ) ) is None
  assert validateTemplate( id_map, with_spec( 'bios_version', { '$min': '2.12.0' } ) ) == [ 'Item "hardware.bios_version" value "2.10.3" is less than "2.12.0"' ]
  assert validateTemplate( id_map, template_base ) is None


def test_validate_template_list_each_and_count():
  id_map = { 'disks': [ { 'isSSD': True, 'capacity': 500 }, { 'isSSD': True, 'capacity': 1000 } ] }

  assert validateTemplate( id_map, { 'disks': [ { 'isSSD': { '$match': 'True' }, 'capacity': { '$any': True } } ] } ) is None
  assert validateTemplate( id_map, { 'disks': { '$each': { '*': { '$any': True } }, '$count': { '$min': 1 } } } ) is None
  assert validateTemplate( id_map, { 'disks': { '$each': { '*': { '$any': True } }, '$count': { '$min': 3 } } } ) == [ 'Item "disks" count 2 is less than 3' ]
  assert validateTemplate( id_map, { 'disks': [ { 'isSSD': { '$match': 'False' }, '*': { '$any': True } } ] } ) == [ 'Item "disks.0.isSSD" value "True" does not match "False"', 'Item "disks.1.isSSD" value "True" does not match "False"' ]


def test_validate_template_dict_count():
  id_map = { 'network': { 'eth0': {}, 'eth1': {} } }

  assert validateTemplate( id_map, { 'network': { '*': { '$any': True }, '$count': { '$min': 2 } } } ) is None
  assert validateTemplate( id_map, { 'network': { '*': { '$any': True }, '$count': { '$min': 3 } } } ) == [ 'Item "network" count 2 is less than 3' ]


def test_validate_template_eq():
  id_map = { 'hardware': { 'total_cpu_count': 32, 'bios_version': '2.10.3', 'flag': True } }
  template_base = { 'hardware': { '*': { '$any': True } } }

  def with_spec( name, spec ):
    return { 'hardware': { '*': { '$any': True }, name: spec } }

  assert validateTemplate( id_map, with_spec( 'total_cpu_count', { '$eq': 32 } ) ) is None
  assert validateTemplate( id_map, with_spec( 'total_cpu_count', { '$eq': 16 } ) ) == [ 'Item "hardware.total_cpu_count" value "32" does not equal "16"' ]
  assert validateTemplate( id_map, with_spec( 'bios_version', { '$eq': '2.10.3' } ) ) is None
  assert validateTemplate( id_map, with_spec( 'flag', { '$eq': True } ) ) is None
  assert validateTemplate( id_map, template_base ) is None

  id_map[ 'hardware' ][ 'notes' ] = { 'a': 1 }
  assert validateTemplate( id_map, with_spec( 'notes', { '$eq': 1 } ) ) == [ 'Item "hardware.notes" can not be compared for equality' ]


def test_validate_template_in():
  id_map = { 'disks': { 'SAS 0:0': { 'model': 'ST2000B' } } }

  template = { 'disks': { 'SAS 0:0': { 'model': { '$in': [ 'ST2000A', 'ST2000B', 'ST2000C' ] } } } }
  assert validateTemplate( id_map, template ) is None

  bad_template = { 'disks': { 'SAS 0:0': { 'model': { '$in': [ 'ST2000A', 'ST2000C' ] } } } }
  assert validateTemplate( id_map, bad_template ) == [ 'Item "disks.SAS 0:0.model" value "ST2000B" is not one of [\'ST2000A\', \'ST2000C\']' ]


def test_check_template_bad_in():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { 'model': { '$in': [] } } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { 'model': { '$in': 'not-a-list' } } } )


def test_validate_template_multiple_errors():
  # every mismatch is reported, not just the first -- important for someone bootstrapping a
  # physical machine to see everything wrong in one pass
  id_map = { 'hardware': { 'total_ram': 1024 }, 'network': { 'eth0': {} } }

  errors = validateTemplate( id_map, { 'hardware': { 'total_ram': { '$min': 34359738368 } }, 'network': { 'eth9': { '$any': True } } } )
  assert set( errors ) == { 'Item "hardware.total_ram" value "1024" is less than "34359738368"', 'Item "network.eth9" not found', 'Unexpected item "network.eth0"' }
  assert len( errors ) == 3


def test_validate_template_value_truncated_in_message():
  # id_map content is reported by whatever's bootstrapping, not trusted -- a huge value (or key)
  # must not be able to inflate a single error message without limit
  huge_value = 'A' * 10000
  errors = validateTemplate( { 'x': huge_value }, { 'x': { '$eq': 'expected' } } )
  assert len( errors ) == 1
  assert len( errors[ 0 ] ) < 300
  assert errors[ 0 ].endswith( '...(truncated)" does not equal "expected"' )

  huge_key = 'eth' + 'A' * 10000
  errors = validateTemplate( { 'network': { huge_key: {} } }, { 'network': { 'eth0': { '$any': True } } } )
  unexpected = next( e for e in errors if e.startswith( 'Unexpected item' ) )
  assert len( unexpected ) < 300
  assert unexpected.endswith( '...(truncated)"' )


def test_validate_template_error_count_capped():
  # ditto for the total error count -- an oversized id_map (ex: a list with many elements, all
  # mismatching) shouldn't be able to inflate the response without limit either
  id_map = { 'disks': [ { 'isSSD': False } for _ in range( 1000 ) ] }
  template = { 'disks': [ { 'isSSD': { '$eq': True } } ] }

  errors = validateTemplate( id_map, template )
  assert len( errors ) == 11
  assert errors[ -1 ] == '...and more errors omitted'

  # the cap applies to the dict paths too, both the wildcard walk and the "unexpected key" walk
  id_map = { 'network': { 'eth{0}'.format( i ): { 'mac': 'zzz' } for i in range( 1000 ) } }
  assert len( validateTemplate( id_map, { 'network': { '*': { 'mac': { '$match': '^[0-9a-f:]+$' } } } } ) ) == 11
  assert len( validateTemplate( id_map, { 'network': { 'eth0': { '$any': True } } } ) ) == 11


def test_validate_template_error_cap_does_not_corrupt_contains():
  # the element/key walks stop early once already past the cap -- that must only ever truncate an
  # ALREADY-failing node, never turn a non-empty error list into an empty one, because
  # _checkContainsClause decides a match by "did this sub-validation come back clean". If early
  # abort could empty an error list it would silently turn a $contains non-match into a match.
  id_map = { 'pci': { str( i ): { 'vpd': [ { 'id': 'x' } for _ in range( 1000 ) ] } for i in range( 3 ) } }
  template = { 'pci': { '$contains': { 'vpd': [ { 'id': { '$eq': 'NEVER' } } ] } } }
  assert validateTemplate( id_map, template ) == [ 'Item "pci" does not contain enough items matching $contains (0 found)' ]

  # ...and a genuine match is still found, even alongside a candidate big enough to hit the cap
  id_map = { 'pci': { '0': { 'vpd': [ { 'id': 'FOUND' } ] }, '1': { 'vpd': [ { 'id': 'x' } for _ in range( 1000 ) ] } } }
  template = { 'pci': { '$contains': { 'vpd': [ { 'id': { '$eq': 'FOUND' } } ] } } }
  assert validateTemplate( id_map, template ) is None


def test_validate_template_loose():
  id_map = {
    'hardware': { 'total_ram': 137438953472, 'dmi': { 'System Info': [ { 'Manufacturer': 'Dell Inc.', 'Product Name': 'PowerEdge R640' } ] } },
    'network': { 'eth0': { 'mac': 'aa:bb:cc:dd:ee:ff', 'lldp': { 'name': 'switch1' } } },
    'disks': { 'pci0': { 'isSSD': True } }
  }

  # $loose accepts unnamed keys at every depth below it without needing "*" at each level
  template = { '$loose': True, 'hardware': { 'total_ram': { '$min': 34359738368 } } }
  assert validateTemplate( id_map, template ) is None

  # a descendant can turn strictness back on for its own subtree
  template = { '$loose': True, 'network': { '$loose': False, 'eth0': { '$any': True } } }
  assert validateTemplate( id_map, template ) is None

  id_map[ 'network' ][ 'eth1' ] = { 'mac': '11:22:33:44:55:66' }
  assert validateTemplate( id_map, template ) == [ 'Unexpected item "network.eth1"' ]


def test_validate_template_contains():
  id_map = {
    'pci': {
      '0000:01:00.0': { 'vendor': 4318, 'device': 4854, 'vpd': [ { 'id': 'PN', 'value': 'XYZ123' } ] },
      '0000:02:00.0': { 'vendor': 32902, 'device': 4321, 'vpd': [] }
    },
    'disks': [ { 'isSSD': True, 'capacity': 500 }, { 'isSSD': False, 'capacity': 4000 } ]
  }

  # existential match: at least one pci device has this vendor/device, wherever its address is
  template = { 'pci': { '*': { '$any': True }, '$contains': { 'vendor': { '$match': '4318' }, 'device': { '$match': '4854' }, '*': { '$any': True } } }, 'disks': { '$any': True } }
  assert validateTemplate( id_map, template ) is None

  # not present -> a single, clear failure (not one per candidate)
  template = { 'pci': { '*': { '$any': True }, '$contains': { 'vendor': { '$match': '9999' }, '*': { '$any': True } } }, 'disks': { '$any': True } }
  assert validateTemplate( id_map, template ) == [ 'Item "pci" does not contain enough items matching $contains (0 found)' ]

  # nested $contains -- recursive tree descent: a specific vpd entry inside a specific pci device
  template = {
    'pci': {
      '*': { '$any': True },
      '$contains': { 'vendor': { '$match': '4318' }, '*': { '$any': True }, 'vpd': { '$contains': { 'id': { '$match': 'PN' }, 'value': { '$match': 'XYZ.*' } } } }
    },
    'disks': { '$any': True }
  }
  assert validateTemplate( id_map, template ) is None

  # $contains on a list, combined with $each ("every disk must look like a disk, and at least one must be a >=1TB SSD")
  template = {
    'pci': { '$any': True },
    'disks': { '$each': { '*': { '$any': True } }, '$contains': { 'isSSD': { '$match': 'True' }, 'capacity': { '$min': 1000 } } }
  }
  assert validateTemplate( id_map, template ) == [ 'Item "disks" does not contain enough items matching $contains (0 found)' ]

  template[ 'disks' ][ '$contains' ] = { 'isSSD': { '$match': 'True' }, 'capacity': { '$min': 100 } }
  assert validateTemplate( id_map, template ) is None


def test_validate_template_or():
  # "$or": the value must satisfy at least one of several alternative sub-templates -- ex: a DMI
  # field reported under one of two differently-spelled keys depending on vendor/dmidecode version
  id_map = { 'entry': { 'Manufacturer': 'Acme', 'Product_Name': 'SMT-5500' } }

  template = { '$loose': True, 'entry': { '$or': [
    { 'Product Name': { '$eq': 'SMT-5500' } },
    { 'Product_Name': { '$eq': 'SMT-5500' } }
  ] } }
  assert validateTemplate( id_map, template ) is None

  id_map[ 'entry' ] = { 'Manufacturer': 'Acme', 'Product Name': 'SMT-5500' }
  assert validateTemplate( id_map, template ) is None

  id_map[ 'entry' ][ 'Product Name' ] = 'WRONG'
  assert validateTemplate( id_map, template ) == [ 'Item "entry" does not match any of the 2 "$or" alternatives' ]


def test_check_template_bad_or():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'entry': { '$or': [] } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'entry': { '$or': 'not-a-list' } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'entry': { '$or': [ { '$mtach': '.*' } ] } } )


def test_check_template_dead_sibling():
  # "$any"/"$each"/"$or"/"$match"/"$min"/"$max"/"$eq"/"$in" all make _validateNode return
  # before it ever looks at anything else in the same dict -- a named key (or "*") sitting next
  # to one of them would silently never be checked, so checkTemplate rejects it up front instead
  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { '$any': True, 'vendor': { '$eq': 'x' } } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'disks': { '$each': { '$any': True }, 'bogus': { '$eq': 'x' } } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { '$or': [ { '$any': True } ], 'bogus': { '$eq': 'x' } } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { 'vendor': { '$match': '.*', 'nested': { '$eq': 'x' } } } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { 'x': { '*': { '$any': True }, '$eq': 1 } } } )

  # legitimate combinations (bookkeeping keys, not named/wildcard keys) still pass
  checkTemplate( { 'hardware': { '$loose': True, 'x': { '$eq': 1 } } } )
  checkTemplate( { 'disks': { '$each': { 'isSSD': { '$any': True } }, '$count': 2 } } )
  checkTemplate( { 'pci': { '*': { '$any': True }, '$contains': { 'vendor': { '$eq': 1 } } } } )


def test_check_template_dead_sibling_count_and_contains():
  # unlike "$each" (which explicitly reads "$count"/"$contains" out of its own template),
  # "$any"/"$or"/the leaf specs never look at "$count"/"$contains" at all -- so those two would
  # also go silently dead next to them, the same way a named/wildcard key would
  with pytest.raises( TemplateError ):
    checkTemplate( { 'network': { '$any': True, '$count': 2 } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'network': { '$or': [ { '$any': True } ], '$count': 2 } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'network': { '$any': True, '$contains': { '$any': True } } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { 'x': { '$eq': 1, '$count': 2 } } } )

  # "$loose" is exempt even here -- "$each"/"$or" both thread it into their own recursion
  checkTemplate( { 'disks': { '$each': { '$any': True }, '$loose': True } } )
  checkTemplate( { 'entry': { '$loose': True, '$or': [ { '$any': True } ] } } )


def test_check_template_bad_optional_exists_any():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'x': { '$exists': 'False' } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'x': { '$optional': 1 } } )

  with pytest.raises( TemplateError ):
    checkTemplate( { 'x': { '$any': False } } )

  checkTemplate( { 'x': { '$exists': False } } )
  checkTemplate( { 'x': { '$optional': True } } )
  checkTemplate( { 'x': { '$any': True } } )


def test_validate_template_contains_count_exact():
  # "$contains_count" (single sub_template form) also accepts an exact int, not just $min/$max
  id_map = { 'network': { 'eth0': { 'primary': True }, 'eth1': { 'primary': False } } }

  template = { 'network': { '$contains': { 'primary': { '$eq': True } }, '$contains_count': 1 } }
  assert validateTemplate( id_map, template ) is None

  id_map[ 'network' ][ 'eth1' ][ 'primary' ] = True
  assert validateTemplate( id_map, template ) == [ 'Item "network" does not contain enough items matching $contains (2 found)' ]


def test_validate_template_contains_multiple_clauses():
  # a single "$contains" can only express one existence+count requirement -- "$contains" as a
  # list lets several independent ones apply to the same collection at once, ex: exactly 2
  # mellanox cards AND exactly 4 nvidia gpus, both keyed unpredictably by pci bus address
  id_map = {
    'pci': {
      '0000:01:00.0': { 'vendor': 5555, 'device': 4117 },
      '0000:02:00.0': { 'vendor': 5555, 'device': 4117 },
      '0000:03:00.0': { 'vendor': 4318, 'device': 4854 },
      '0000:04:00.0': { 'vendor': 4318, 'device': 4854 },
      '0000:05:00.0': { 'vendor': 4318, 'device': 4854 },
      '0000:06:00.0': { 'vendor': 4318, 'device': 4854 }
    }
  }

  template = {
    'pci': {
      '*': { '$any': True },
      '$contains': [
        { '$template': { 'vendor': { '$match': '5555' }, '*': { '$any': True } }, '$count': 2 },
        { '$template': { 'vendor': { '$match': '4318' }, '*': { '$any': True } }, '$count': 4 }
      ]
    }
  }
  assert validateTemplate( id_map, template ) is None

  # drop a GPU -- only 3 nvidia devices now, mellanox count is still fine
  del id_map[ 'pci' ][ '0000:06:00.0' ]
  assert validateTemplate( id_map, template ) == [ 'Item "pci" does not contain enough items matching $contains[1] (3 found)' ]


def test_check_template_ok():
  template = {
    '$loose': True,
    'hardware': { 'total_ram': { '$min': 34359738368 } },
    'network': { '*': { 'mac': { '$match': '^[0-9a-f:]+$' } }, '$count': { '$min': 1 } },
    'disks': [ { 'isSSD': { '$match': 'True' } } ],
    'pci': { '$contains': { 'vendor': { '$match': '4318' } }, '$contains_count': { '$min': 1 } }
  }
  checkTemplate( template )


def test_check_template_bad_key():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { '$mtach': '.*' } } )


def test_check_template_bad_type():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { '$type': 'complex' } } )


def test_check_template_bad_regex():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { 'vendor': { '$match': '(' } } } )


def test_check_template_bad_list():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'disks': [ {}, {} ] } )


def test_check_template_bad_loose():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'hardware': { '$loose': 'yes' } } )


def test_check_template_bad_contains():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'pci': { '$contains': { '$mtach': '.*' } } } )


def test_check_template_bad_contains_count():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'pci': { '$contains': { '$any': True }, '$contains_count': { '$bogus': 1 } } } )


def test_check_template_contains_clause_list_ok():
  template = {
    'pci': {
      '$contains': [
        { '$template': { 'vendor': { '$match': '5555' } }, '$count': 2 },
        { '$template': { 'vendor': { '$match': '4318' } } }  # $count optional, defaults to $min: 1
      ]
    }
  }
  checkTemplate( template )


def test_check_template_bad_contains_clause_missing_template():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'pci': { '$contains': [ { '$count': 2 } ] } } )


def test_check_template_bad_contains_clause_extra_key():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'pci': { '$contains': [ { '$template': { '$any': True }, '$bogus': 1 } ] } } )


def test_check_template_bad_contains_clause_bad_subtemplate():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'pci': { '$contains': [ { '$template': { '$mtach': '.*' } } ] } } )


def test_check_template_bad_contains_empty_list():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'pci': { '$contains': [] } } )


def test_check_template_bad_contains_list_with_contains_count():
  with pytest.raises( TemplateError ):
    checkTemplate( { 'pci': { '$contains': [ { '$template': { '$any': True } } ], '$contains_count': 1 } } )
