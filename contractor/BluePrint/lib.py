import re
import operator

# validation_template format
# ---------------------------
# A validation_template is a plain dict (JSON safe) shaped like the id_map it will be
# checked against -- see contractor/BluePrint/lib.py's caller (FoundationBluePrint.validateIdMap)
# and disks/disks/bootstrap/root/bootstrap.py for what an id_map looks like, ex:
#
#   {
#     'hardware': {
#       'dmi': {
#         'System Info': [ { 'Manufacturer': 'Dell Inc.', 'Product Name': 'PowerEdge R640', ... } ],
#         'Processor Information': [ { 'Version': 'Intel(R) Xeon(R) ...', 'Core Count': '16', ... }, { ... } ],
#         ...
#       },
#       'pci': { '0000:01:00.0': { 'vendor': 4318, 'device': 4854, 'vpd': [ ... ] }, ... },
#       'total_ram': 137438953472,
#       'total_cpu_count': 32,
#       'total_cpu_sockets': 2
#     },
#     'network': { 'eth0': { 'mac': 'aa:bb:cc:dd:ee:ff', 'primary': True }, ... },
#     'disks': { 'SAS 0:0': { 'model': '...', 'capacity': 500107862016, 'isSSD': True, ... }, ... }
#   }
#
# NOTE: 'disks' is keyed by the drive's location (a stable, physical-slot address, ex: 'SAS
# 0:0', 'NVME 1:0', 'MegaRAID 0:0:2' -- see libdrive's Port classes for the exact formats), not
# a bare list -- the disk enumerator's addressing is consistent across boots/reinstalls, so
# specific bays can be pinned exactly the same way 'network' and 'pci' entries can.
#
# Every node in the template is one of:
#
#  * a "dict node" -- a plain dict (no "$"-prefixed keys, or only bookkeeping "$" keys, see
#    below). Its keys are matched against the keys of the dict found at the same spot in the
#    id_map:
#      - a literal key must be present in the id_map (unless its sub-template has "$optional": True)
#      - the special key "*" is a wildcard/catch-all: its sub-template is applied to every
#        id_map key at this level that isn't otherwise named explicitly
#      - matching is exact by default: any id_map key at this level that is neither named
#        explicitly nor covered by "*" is an error -- this is what makes the template "match
#        exactly". Use "*" (with a permissive sub-template, see "$any" below) to soak up one
#        level of unnamed keys, or "$loose" (below) to soak up every level under a node at once.
#      - a side effect of exact-by-default: a dict node with no "*" already requires the id_map
#        value to have *exactly* the named keys, no more no less -- so naming every entry you
#        expect (ex: pinning every disk bay by address) already implies an exact count for free,
#        no separate "$count" needed. This only holds where the node is NOT "$loose" (inherited
#        or otherwise) -- "$loose" turns this check off along with the "no extra keys" check it's
#        a side effect of, since "$loose" means exactly "there may be more here that I don't
#        care about". If you want a branch to stay exact (and get the implicit count) while an
#        ancestor is "$loose", override it there with "$loose": False.
#
#  * a "list node" -- either the shorthand `[ sub_template ]` (a list containing exactly one
#    template) or `{ "$each": sub_template, "$count": ... }`. The id_map value must be a list;
#    every element is checked against sub_template ("for all" / universal match), and "$count"
#    (see below) can constrain how many elements there are. Element order is not significant.
#
#  * a "leaf/spec node" -- a dict using one or more of the reserved "$" keys below to constrain
#    a scalar (or, for "$count", a list/dict) value directly:
#      - "$match":  regex, checked with re.fullmatch() against str(value). The pattern is
#                  template-author-controlled, but the value it's matched against is not -- it
#                  comes from whatever the hardware/bootstrap client reported, ie. an untrusted
#                  machine's own claims about itself. Avoid patterns with nested quantifiers (ex:
#                  "(a+)+b") that are vulnerable to catastrophic backtracking: a crafted value in
#                  any matched field (Product Name, model, mac, ...) could otherwise tie up the
#                  request thread evaluating it.
#      - "$min"/"$max": inclusive bound. The comparison first tries numeric, then dotted
#                  version-style ("1.12.3"), then falls back to plain string comparison --
#                  so this covers raw numbers, version numbers, and model numbers. Both can be
#                  given on the same leaf to constrain a value to a range, ex: a disk between
#                  1.8TB and 2.2TB is { "$min": 1800000000000, "$max": 2200000000000 } -- there
#                  is no separate "$between", $min+$max together already do that
#
#                  CAVEAT: the version-style comparison only converts a dotted segment to an int
#                  if the *entire* segment is digits -- a segment mixing letters and digits (ex:
#                  a firmware version reported as "v9.0.0") is left as a plain string forever, and
#                  once that happens the whole tuple falls back to a per-segment string compare,
#                  which is NOT numeric ordering: "v9.0.0" >= "v10.0.0" is considered TRUE (because
#                  the string "v9" sorts after "v10"), even though 9 < 10. This bites the first
#                  version field that happens to carry a letter prefix -- if a field's versions can
#                  do that, either normalize the prefix away before templating (a "$match" can
#                  reject a bad prefix, but can't strip one for "$min"/"$max"/"$eq" to compare
#                  against), or confirm the field is always purely dotted-numeric first.
#      - "$eq":     exact match against a single value, using the same numeric/version/string
#                  comparison chain as "$min"/"$max" -- the concise way to say "exactly this",
#                  ex: { "$eq": 32 } for a cpu count, instead of { "$min": 32, "$max": 32 }
#      - "$in":     [ value, ... ] -- exact match against any one of a list of values, using the
#                  same comparison chain as "$eq". This is the concise way to say "one of these
#                  literal options" (ex: one of 3 acceptable model numbers) without hand-building
#                  an "A|B|C" "$match" regex, which needs manual escaping if an option contains
#                  regex metacharacters (parens, dots, ...)
#
#                  NOTE: because "$min"/"$max"/"$eq"/"$in" all go through that same numeric ->
#                  version -> string fallback, none of them are type-checked -- 32 (int) and "32"
#                  (str) compare equal (both parse numerically), and so do "2.10.3" and "2.10.3 "
#                  after any of the three stages matches. The one type "$eq"/"$in" don't quietly
#                  coerce across is bool: True/False are explicitly excluded from the numeric
#                  stage, so { "$eq": 1 } does NOT match the value True (it falls through to
#                  comparing the strings "True" and "1", which differ) -- use { "$match": "True"
#                  } or { "$eq": True } for booleans. If a field's exact type matters (ex: telling
#                  a numeric-looking string apart from an actual number), pair the leaf with
#                  "$type" -- it is checked first and short-circuits before "$eq"/"$min"/etc. run,
#                  so { "$type": "str", "$eq": "32" } rejects the int 32 even though a bare
#                  { "$eq": "32" } would accept it.
#      - "$type":   one of str/int/float/number/bool/list/dict/null
#      - "$count":  either an exact int, or { "$min": n, "$max": m }; checks len(value) -- for
#                  a list node this is the number of elements, for a dict node the number of keys.
#                  Only needed when you're not naming every key (ex: under "*" or "$loose", or on
#                  a "$each"-validated list) -- an exact (non-"$loose") dict node with every key
#                  named and no "*" already gets an exact count for free, see the dict node notes
#                  above
#      - "$any":    True -- accept anything (still requires the key to be present unless
#                  combined with "$optional"). Must be exactly `True` -- "$any": False is rejected
#                  by checkTemplate() rather than silently doing the opposite of what it says. Note
#                  an empty dict `{}` is NOT the same thing -- with no "*" and no "$any" it is a
#                  dict node requiring the id_map value to be an object with zero keys (a
#                  consequence of exact-match being the default)
#
#  Any node (dict/list/leaf) may also set:
#      - "$optional": True  -- do not fail if the item is missing (default: required; must be an
#                  actual bool). A template containing *only* "$optional" (and/or "$exists") --
#                  i.e. no other constraint -- means "I only care whether it's present": it is
#                  treated as "$any" if the item is there, rather than requiring the value to be
#                  an empty dict (which the equivalent-looking bare `{}` above still does).
#      - "$exists": False   -- fail if the item *is* present (rarely needed; must be an actual
#                  bool, not just a truthy value -- a stray string like "$exists": "False" would
#                  otherwise silently mean the opposite of what it looks like it says)
#      - "$loose": True  -- for this node and every dict node nested beneath it (unless a
#                  descendant sets "$loose": False), any key that isn't named explicitly is
#                  accepted without needing a "*" wildcard. This is the shortcut for the common
#                  case of "match a branch or two exactly, don't care about the rest": set
#                  "$loose": True near the root and only list the branches you actually check,
#                  instead of adding "*": { "$any": True } at every intermediate level. Remember
#                  it's inherited: if a branch under a "$loose" root still needs to be exact
#                  (ex: to get the implicit exact-count-from-named-keys behavior above), set
#                  "$loose": False on that branch to opt back into strict matching there.
#      - "$contains": sub_template  -- existential match, valid on list AND dict nodes: instead
#                  of requiring every element/value to satisfy sub_template (that's what "*"
#                  and "$each" do), requires that *some* of them do. Useful for collections whose
#                  keys/order aren't something a template can pin down in advance -- e.g. "pci"
#                  is keyed by PCI bus address, which can differ by slot population even between
#                  otherwise-identical machines, so "there is a device matching X somewhere in
#                  pci" has to be existential rather than a literal key. Can be combined with "*"
#                  or "$each" on the same node (e.g. "every pci entry must look like a pci entry,
#                  and at least one of them must be this specific GPU"). sub_template is checked
#                  the same recursive way as any other node, so it can itself contain nested
#                  "$contains" (e.g. asserting a specific vpd entry exists inside a specific pci
#                  device) without any special-casing.
#
#                  "$contains" can also be a *list* of clauses instead of a single sub_template,
#                  each shaped { "$template": sub_template, "$count": count_spec } ("$count" on a
#                  clause defaults to { "$min": 1 }, same as top-level "$contains_count"). This is
#                  how to assert several independent existence+count requirements against the
#                  same collection at once, ex: "exactly 2 Mellanox cards AND exactly 4 Nvidia
#                  GPUs" on the same "pci" dict -- a single "$contains" can only express one such
#                  requirement, since a dict can't repeat the "$contains" key. When "$contains" is
#                  a list, "$contains_count" is not used (put "$count" on each clause instead).
#      - "$contains_count": how many matches "$contains" requires when "$contains" is a single
#                  sub_template (not a list of clauses) -- same shape as "$count" (an exact int,
#                  or { "$min": n, "$max": m }). Defaults to { "$min": 1 }.
#      - "$or": [ sub_template, ... ]  -- the value at this node must satisfy at least one of the
#                  listed sub_templates (each checked the same recursive way as any other node,
#                  so they can be full dict/list/leaf templates, not just leaf specs). This is
#                  different from "$contains": "$contains" picks one-or-more *elements* out of a
#                  collection, "$or" picks one-or-more *alternative shapes* for a single value.
#                  The main use is tolerating a field that can legitimately show up in more than
#                  one shape, ex: a DMI field name that's spelled with a space on some vendors'
#                  dmidecode output and an underscore on others -- "$or": [ { "Product Name": {
#                  "$eq": "..." } }, { "Product_Name": { "$eq": "..." } } ] passes if either key is
#                  present with that value. Each alternative is checked as its own dict node, so
#                  it needs "$loose" (inherited or set locally) if it shouldn't also fail on the
#                  other alternative's key being "unexpected".
#
# "$any"/"$each"/"$or" and the leaf specs ("$match"/"$min"/"$max"/"$eq"/"$in") each take over their
# node's matching almost entirely -- a named key or "*" sitting next to one of them at the same
# level would silently never be checked (the node returns before ever looking at it), and so would
# "$count"/"$contains" next to anything except "$each" ("$each" is the only one of these that
# actually reads "$count"/"$contains" back out of its own template). checkTemplate() rejects all of
# those combinations outright rather than let a template through that looks like it checks
# something it doesn't. "$type"/"$optional"/"$exists" are always safe alongside any of the above
# (checked before dispatch gets there), and so is "$loose" ("$each"/"$or" both thread it into their
# own recursion, and it's a no-op rather than a silent lie for "$any"/the leaf specs, which never
# recurse into anything to inherit it).
#
# Paths in error messages are dotted, e.g. "hardware.dmi.System Info.0.Manufacturer".
#
# validateTemplate() returns None if the id_map matches, or a list of every mismatch message it
# found (it does not stop at the first problem) -- this is meant to let someone bootstrapping
# a physical machine see everything wrong in one pass instead of fixing one problem per reboot.
#
# id_map is reported by whatever's bootstrapping, not trusted, so both dimensions of that list are
# bounded regardless of how large or malformed id_map is: any single key or value that lands in a
# message is truncated to _MAX_MESSAGE_VALUE_LEN, and no more than _MAX_ERRORS mismatches are
# collected (a final "...and more errors omitted" entry says so). The element/key loops stop walking
# as soon as they are already past that limit rather than collecting everything and trimming at the
# end, so a huge or maliciously-shaped id_map (a giant string in some field, a list with hundreds of
# thousands of elements) costs neither the memory nor the CPU to format the messages that would just
# be discarded. That is also why the "omitted" entry carries no count -- the walk stopped early, so
# the true total was never determined.
#
# Example:
#
#   {
#     '$loose': True,   # don't care about anything not named below, at any depth
#     'hardware': {
#       'dmi': {
#         'System Info': [ { 'Manufacturer': { '$match': '^Dell Inc\\.$' } } ]
#       },
#       'total_ram': { '$min': 34359738368 },
#       'total_cpu_count': { '$min': 8 },
#       'pci': {
#         '$contains': [                                                            # exactly 2 mellanox nics...
#           { '$template': { 'vendor': { '$match': '5555' } }, '$count': 2 },
#           { '$template': { 'vendor': { '$match': '4318' } }, '$count': 4 }        # ...and exactly 4 nvidia gpus
#         ]
#       }
#     },
#     'network': {
#       '*': { 'mac': { '$match': '^[0-9a-f]{2}(:[0-9a-f]{2}){5}$' } },
#       '$count': { '$min': 2 }
#     },
#     'disks': {
#       'SAS 0:0': { 'isSSD': { '$match': 'True' } },  # boot bay pinned exactly
#       '*': { 'isSSD': { '$any': True } }              # remove this "*" to also require there be no other disks
#     }
#   }
#
# A few more worked scenarios (each stands alone, not building on the others):
#
# 1) Only cpu count, memory amount, and DMI "System Info" > "Product Name" matter -- everything
#    else (BIOS versions, chassis info, other DMI groups, disks, network...) is unconstrained.
#    Also shows: "$type" paired with "$eq" (reject a numeric-looking string where an actual int
#    is expected -- see the "$eq"/"$in" NOTE above), and the explicit "$each"/"$count" list-node
#    form (as opposed to the "[ sub_template ]" shorthand used for "System Info") to require
#    exactly 2 "Processor Information" entries, each reporting a 16-core cpu:
#
#      {
#        '$loose': True,
#        'hardware': {
#          'total_cpu_count': { '$type': 'int', '$eq': 32 },
#          'total_ram': { '$eq': 137438953472 },
#          'dmi': {
#            'System Info': [ { 'Product Name': { '$eq': 'PowerEdge R640' } } ],
#            'Processor Information': { '$each': { 'Core Count': { '$eq': '16' } }, '$count': 2 }
#          }
#        }
#      }
#
# 2) Exactly 2 disks, addressed by bay so bay 0 is unconstrained and bay 1 must be a 2TB SSD
#    whose model is one of three part numbers. Naming both bay addresses would, on its own,
#    already mean "no other disks allowed" (see the dict node notes above) -- but that only holds
#    for a non-"$loose" node, and this whole template is "$loose" from the root down so unnamed
#    bays (and unnamed fields within a bay, like devpath/pcipath/isVirtualDisk) are allowed by
#    default. An explicit "$count" re-adds the "exactly this many" check on top of "$loose"
#    without having to fight the inherited looseness at every level:
#
#      {
#        '$loose': True,
#        'disks': {
#          '$count': 2,
#          'SAS 0:0': { '$any': True },        # just needs to be present; contents don't matter
#          'SAS 0:1': {
#            'isSSD': { '$eq': True },
#            'capacity': { '$min': 2000000000000, '$max': 2200000000000 },
#            'model': { '$in': [ 'ST2000A', 'ST2000B', 'ST2000C' ] }
#          }
#        }
#      }
#
#    (see scenario 4 below for why "$count" is what supplies the "exactly" here, not the naming)
#
# 3) Exactly 2 Mellanox NICs and 4 Nvidia GPUs somewhere in "pci" (bus addresses vary by slot
#    population, so this has to be existential, not literal keys) -- this is the root "Example"
#    above, repeated here for side-by-side comparison with the others. Also adds a second,
#    independent existential check on a different collection ("network" has a primary interface
#    somewhere in it, address unknown) using the single-sub_template form of "$contains" plus an
#    explicit "$contains_count" -- as opposed to the list-of-clauses form "pci" needs here, since
#    "network" only has one existence requirement, not several:
#
#      {
#        '$loose': True,
#        'hardware': {
#          'pci': {
#            '$contains': [
#              { '$template': { 'vendor': { '$eq': 5555 } }, '$count': 2 },   # 2 mellanox...
#              { '$template': { 'vendor': { '$eq': 4318 } }, '$count': 4 }    # ...4 nvidia
#            ]
#          }
#        },
#        'network': { '$contains': { 'primary': { '$eq': True } }, '$contains_count': 1 }
#      }
#
# 4) CPU count and memory amount exact, at least 3 disks total but only the first bay's details
#    matter -- "$loose": True on "disks" (so unnamed bays are allowed) plus an explicit "$count"
#    (naming only one bay under a loose node doesn't imply a minimum the way it does under a
#    strict one, since a loose node's key list was never meant to be exhaustive -- this is the
#    same reason scenario 2 needs its own explicit "$count" too, just with an exact int there
#    instead of a "$min"). Also adds three more real-world wrinkles: "$optional" bare (some boxes
#    don't report a socket count at all -- fine either way), "$optional" with a constraint (an
#    NVMe cache module that may or may not be installed, but must be an SSD if it is), and
#    "$exists": False (this platform must NOT have a legacy IDE-addressed disk):
#
#      {
#        '$loose': True,
#        'hardware': {
#          'total_cpu_count': { '$eq': 32 },
#          'total_ram': { '$eq': 137438953472 },
#          'total_cpu_sockets': { '$optional': True }
#        },
#        'disks': {
#          '$count': { '$min': 3 },
#          'SAS 0:0': { 'isSSD': { '$eq': True } },
#          'NVME 0:0': { '$optional': True, 'isSSD': { '$eq': True } },
#          'IDE 0:0': { '$exists': False }
#        }
#      }
#
# 5) Exactly 4 network cards, and the first one's mac address starts with "08:00" -- "$match" is
#    a regex, so a prefix check is just an unanchored-at-the-end pattern, and "$count" on the
#    "network" dict (rather than naming every interface) pins the total:
#
#      {
#        '$loose': True,
#        'network': {
#          '$count': 4,
#          'eth0': { 'mac': { '$match': '08:00:.*' } }
#        }
#      }
#
# 6) DMI "System Info"'s "Product Name" equals "SMT-5500" -- except some dmidecode versions
#    report that field as "Product_Name" (underscore) instead, and either spelling should count.
#    This is what "$or" is for -- two alternative shapes for the same "System Info" entry, one
#    per possible key spelling:
#
#      {
#        '$loose': True,
#        'hardware': {
#          'dmi': {
#            'System Info': [ { '$or': [
#              { 'Product Name': { '$eq': 'SMT-5500' } },
#              { 'Product_Name': { '$eq': 'SMT-5500' } }
#            ] } ]
#          }
#        }
#      }


class TemplateError( Exception ):  # the validation_template itself is malformed, not an id_map mismatch
  pass


_MISSING = object()
WILDCARD = '*'

_TYPE_MAP = { 'str': str, 'int': int, 'float': float, 'bool': bool, 'list': list, 'dict': dict }

_VALID_TYPES = { 'number', 'null' } | set( _TYPE_MAP )
_RESERVED_KEYS = { '$optional', '$exists', '$any', '$type', '$match', '$min', '$max', '$eq', '$in', '$count', '$each', '$loose', '$contains', '$contains_count', '$or' }
_BOOKKEEPING_KEYS = ( '$optional', '$exists', '$type', '$count', '$loose', '$contains', '$contains_count' )
_EXCLUSIVE_DISPATCH_KEYS = { '$any', '$each', '$or', '$match', '$min', '$max', '$eq', '$in' }  # presence of any of these makes _validateNode return without ever looking at most of what else is in the same dict
_ALWAYS_SAFE_WITH_EXCLUSIVE = { '$type', '$optional', '$exists', '$loose' }  # consulted before dispatch (or, for "$loose", threaded into "$each"/"$or"'s own recursion), so these never go dead alongside an exclusive key
_EXCLUSIVE_CONSUMES = { '$each': { '$count', '$contains' } }  # keys an exclusive key actually reads out of its own template, beyond _ALWAYS_SAFE_WITH_EXCLUSIVE ("$any"/"$or"/leaf specs consume nothing extra -- "$count"/"$contains" alongside those would silently never be applied)

_MAX_MESSAGE_VALUE_LEN = 200  # id_map keys/values are reported by whatever's bootstrapping, not trusted -- bound how much of one can land in a single message
_MAX_ERRORS = 10  # past this many mismatches it's the wrong machine entirely, not a fixable discrepancy, so there is nothing to gain by finding the rest. The element/key loops stop walking once they are already past this (not just trimming at the end) -- that is what keeps a huge or malformed id_map from costing the CPU and memory to format a message per element before the extras get discarded


def _fmt( value ):  # stringify+truncate a value before it goes into a message -- see _MAX_MESSAGE_VALUE_LEN
  text = str( value )
  if len( text ) > _MAX_MESSAGE_VALUE_LEN:
    return text[ :_MAX_MESSAGE_VALUE_LEN ] + '...(truncated)'

  return text


def _join( path, part ):
  return '{0}.{1}'.format( path, _fmt( part ) ) if path else _fmt( part )


def _asNumber( value ):
  if isinstance( value, bool ):
    raise TypeError( 'bool is not a number' )

  if isinstance( value, ( int, float ) ):
    return value

  return float( value )


def _asVersion( value ):
  parts = re.split( r'[.\-_]', str( value ) )
  return tuple( int( part ) if part.isdigit() else part for part in parts )


def _compareBound( value, bound, op ):
  try:
    return op( _asNumber( value ), _asNumber( bound ) )
  except ( TypeError, ValueError ):
    pass

  try:
    return op( _asVersion( value ), _asVersion( bound ) )
  except TypeError:
    pass

  return op( str( value ), str( bound ) )


def _checkType( value, type_name, path ):
  if type_name == 'number':
    if isinstance( value, bool ) or not isinstance( value, ( int, float ) ):
      return [ 'Item "{0}" is not a number'.format( path ) ]
    return []

  if type_name == 'null':
    if value is not None:
      return [ 'Item "{0}" is not null'.format( path ) ]
    return []

  py_type = _TYPE_MAP[ type_name ]
  if isinstance( value, bool ) and py_type is not bool:
    return [ 'Item "{0}" is not of type "{1}"'.format( path, type_name ) ]

  if not isinstance( value, py_type ):
    return [ 'Item "{0}" is not of type "{1}"'.format( path, type_name ) ]

  return []


def _checkCount( count, count_spec, path ):
  if isinstance( count_spec, dict ):
    if '$min' in count_spec and count < count_spec[ '$min' ]:
      return [ 'Item "{0}" count {1} is less than {2}'.format( path, count, count_spec[ '$min' ] ) ]

    if '$max' in count_spec and count > count_spec[ '$max' ]:
      return [ 'Item "{0}" count {1} is greater than {2}'.format( path, count, count_spec[ '$max' ] ) ]

    return []

  if count != count_spec:
    return [ 'Item "{0}" count {1} does not equal {2}'.format( path, count, count_spec ) ]

  return []


def _checkLeaf( value, template, path ):
  errors = []

  if '$match' in template:
    if isinstance( value, ( list, dict ) ):
      errors.append( 'Item "{0}" can not be matched against a pattern'.format( path ) )
    elif not re.fullmatch( template[ '$match' ], str( value ) ):  # match against the real, untruncated value -- only the message uses _fmt()
      errors.append( 'Item "{0}" value "{1}" does not match "{2}"'.format( path, _fmt( value ), _fmt( template[ '$match' ] ) ) )

  if '$min' in template and not _compareBound( value, template[ '$min' ], operator.ge ):
    errors.append( 'Item "{0}" value "{1}" is less than "{2}"'.format( path, _fmt( value ), _fmt( template[ '$min' ] ) ) )

  if '$max' in template and not _compareBound( value, template[ '$max' ], operator.le ):
    errors.append( 'Item "{0}" value "{1}" is greater than "{2}"'.format( path, _fmt( value ), _fmt( template[ '$max' ] ) ) )

  if '$eq' in template:
    if isinstance( value, ( list, dict ) ):
      errors.append( 'Item "{0}" can not be compared for equality'.format( path ) )
    elif not _compareBound( value, template[ '$eq' ], operator.eq ):
      errors.append( 'Item "{0}" value "{1}" does not equal "{2}"'.format( path, _fmt( value ), _fmt( template[ '$eq' ] ) ) )

  if '$in' in template:
    options = template[ '$in' ]
    if isinstance( value, ( list, dict ) ):
      errors.append( 'Item "{0}" can not be compared for equality'.format( path ) )
    elif not any( _compareBound( value, option, operator.eq ) for option in options ):
      errors.append( 'Item "{0}" value "{1}" is not one of {2}'.format( path, _fmt( value ), _fmt( options ) ) )

  return errors


def _checkContainsClause( candidates, sub_template, count_spec, path, loose, label ):
  matched = sum( 1 for item in candidates if not _validateNode( item, sub_template, '', loose ) )

  if _checkCount( matched, count_spec, path ):
    return [ 'Item "{0}" does not contain enough items matching {1} ({2} found)'.format( path, label, matched ) ]

  return []


def _checkContains( value, template, path, loose ):
  if not isinstance( value, ( list, dict ) ):
    return [ 'Item "{0}" does not support $contains'.format( path ) ]

  contains = template[ '$contains' ]
  candidates = value if isinstance( value, list ) else list( value.values() )

  if isinstance( contains, list ):  # multiple independent clauses, each with its own count -- ex: "2 of X and 4 of Y"
    errors = []
    for index, clause in enumerate( contains ):
      count_spec = clause.get( '$count', { '$min': 1 } )
      errors += _checkContainsClause( candidates, clause[ '$template' ], count_spec, path, loose, '$contains[{0}]'.format( index ) )
    return errors

  count_spec = template.get( '$contains_count', { '$min': 1 } )
  return _checkContainsClause( candidates, contains, count_spec, path, loose, '$contains' )


def _checkOr( value, template, path, loose ):
  alternatives = template[ '$or' ]

  for alternative in alternatives:
    if not _validateNode( value, alternative, '', loose ):  # a passing alternative's own path/messages don't matter, just whether it passed
      return []

  return [ 'Item "{0}" does not match any of the {1} "$or" alternatives'.format( path, len( alternatives ) ) ]


def _checkList( value, template, path, loose ):
  if not isinstance( value, list ):
    return [ 'Item "{0}" is not a list'.format( path ) ]

  errors = []

  if '$count' in template:
    errors += _checkCount( len( value ), template[ '$count' ], path )

  each = template[ '$each' ]
  for index, item in enumerate( value ):
    if len( errors ) > _MAX_ERRORS:  # see _MAX_ERRORS: stop before formatting a message per remaining element. Only ever triggers once this node is already failing, so it can never turn a non-empty error list into an empty one (which would flip a "$contains" non-match into a match)
      break

    errors += _validateNode( item, each, _join( path, index ), loose )

  if '$contains' in template:
    errors += _checkContains( value, template, path, loose )

  return errors


def _checkDict( value, template, path, loose ):
  if not isinstance( value, dict ):
    return [ 'Item "{0}" is not an object'.format( path ) ]

  literal_keys = [ key for key in template if key != WILDCARD ]  # list, not set: keeps error order deterministic (str hashing is randomized per-process)
  errors = []

  for key in literal_keys:
    if len( errors ) > _MAX_ERRORS:  # see the note in _checkList -- only ever truncates an already-failing node
      break

    errors += _validateNode( value.get( key, _MISSING ), template[ key ], _join( path, key ), loose )

  if WILDCARD in template:
    wildcard = template[ WILDCARD ]
    literal_key_set = set( literal_keys )
    for key, child_value in value.items():
      if len( errors ) > _MAX_ERRORS:
        break

      if key in literal_key_set:
        continue

      errors += _validateNode( child_value, wildcard, _join( path, key ), loose )

  elif not loose:
    extra = sorted( set( value ) - set( literal_keys ) )
    for key in extra:
      if len( errors ) > _MAX_ERRORS:
        break

      errors.append( 'Unexpected item "{0}"'.format( _join( path, key ) ) )

  return errors


def _validateNode( value, template, path, loose ):
  if isinstance( template, list ):
    if len( template ) != 1:
      raise TemplateError( 'list template at "{0}" must contain exactly one entry'.format( path or '<root>' ) )

    template = { '$each': template[ 0 ] }

  if not isinstance( template, dict ):
    raise TemplateError( 'template at "{0}" must be a dict or a single item list'.format( path or '<root>' ) )

  if not template.get( '$exists', True ):
    if value is not _MISSING:
      return [ 'Item "{0}" is not allowed to be present'.format( path ) ]
    return []

  if value is _MISSING:
    if template.get( '$optional', False ):
      return []
    return [ 'Item "{0}" not found'.format( path ) ]

  # a template containing only "$optional"/"$exists" (no other constraint) means "I only care
  # whether it's present" -- without this, it would fall through to the dict-node handling below
  # and wrongly require the value to be an object with zero keys once it *is* present
  if template and set( template ) <= { '$optional', '$exists' }:
    return []

  if '$any' in template:
    return []

  loose = template.get( '$loose', loose )

  if '$type' in template:
    type_errors = _checkType( value, template[ '$type' ], path )
    if type_errors:
      return type_errors

  if '$each' in template:
    return _checkList( value, template, path, loose )

  if '$or' in template:
    return _checkOr( value, template, path, loose )

  if '$match' in template or '$min' in template or '$max' in template or '$eq' in template or '$in' in template:
    return _checkLeaf( value, template, path )

  plain = { k: v for k, v in template.items() if k not in _BOOKKEEPING_KEYS }

  if not plain and any( key in template for key in ( '$type', '$count', '$contains', '$loose' ) ):
    errors = []
    if '$count' in template:
      if not isinstance( value, ( list, dict ) ):
        errors.append( 'Item "{0}" does not support $count'.format( path ) )
      else:
        errors += _checkCount( len( value ), template[ '$count' ], path )

    if '$contains' in template:
      errors += _checkContains( value, template, path, loose )

    return errors

  errors = list( _checkDict( value, plain, path, loose ) )

  if isinstance( value, dict ):
    if '$count' in template:
      errors += _checkCount( len( value ), template[ '$count' ], path )

    if '$contains' in template:
      errors += _checkContains( value, template, path, loose )

  return errors


def validateTemplate( id_map, validation_template ):  # returns a list of every mismatch message, or None if id_map matches
  if not isinstance( validation_template, dict ):
    raise TemplateError( 'validation_template must be a dict' )

  checkTemplate( validation_template )  # always re-sanity-check the template's own shape before matching against it, in case it reached us without going through FoundationBluePrint.clean() first (ex: a fixture, a direct DB edit, an old row from before some rule existed) -- a malformed template should fail as a clean TemplateError here, not as a raw KeyError/re.error (or, worse, a silently wrong match) partway through _validateNode

  errors = _validateNode( id_map, validation_template, '', False )
  if not errors:
    return None

  if len( errors ) > _MAX_ERRORS:  # no exact count here on purpose: the loops above stop walking once they are already past the limit, so the true total was never counted -- see _MAX_ERRORS
    errors = errors[ :_MAX_ERRORS ] + [ '...and more errors omitted' ]

  return errors


def _checkCountSpec( count_spec, key, path ):
  if isinstance( count_spec, dict ) and set( count_spec ) - { '$min', '$max' }:
    raise TemplateError( '{0} at "{1}" must only contain $min/$max'.format( key, path or '<root>' ) )


def checkTemplate( template, path='' ):  # sanity check the shape of a validation_template itself, ie: catch typos/authoring mistakes early
  if isinstance( template, list ):
    if len( template ) != 1:
      raise TemplateError( 'list template at "{0}" must contain exactly one entry'.format( path or '<root>' ) )

    checkTemplate( template[ 0 ], _join( path, '[]' ) )
    return

  if not isinstance( template, dict ):
    raise TemplateError( 'template at "{0}" must be a dict or a single item list'.format( path or '<root>' ) )

  for key in template:
    if isinstance( key, str ) and key.startswith( '$' ) and key not in _RESERVED_KEYS:
      raise TemplateError( 'unknown key "{0}" at "{1}"'.format( key, path or '<root>' ) )

  exclusive_used = _EXCLUSIVE_DISPATCH_KEYS & set( template )
  if exclusive_used:
    consumed = set()
    for key in exclusive_used:
      consumed |= _EXCLUSIVE_CONSUMES.get( key, set() )

    allowed = _EXCLUSIVE_DISPATCH_KEYS | _ALWAYS_SAFE_WITH_EXCLUSIVE | consumed
    dead_keys = sorted( key for key in template if key not in allowed )
    if dead_keys:
      raise TemplateError( '{0} at "{1}" would never be checked alongside {2}'.format( dead_keys, path or '<root>', sorted( exclusive_used ) ) )

  if '$optional' in template and not isinstance( template[ '$optional' ], bool ):
    raise TemplateError( '$optional at "{0}" must be a bool'.format( path or '<root>' ) )

  if '$exists' in template and not isinstance( template[ '$exists' ], bool ):
    raise TemplateError( '$exists at "{0}" must be a bool'.format( path or '<root>' ) )

  if '$any' in template and template[ '$any' ] is not True:
    raise TemplateError( '$any at "{0}" must be True'.format( path or '<root>' ) )

  if '$type' in template and template[ '$type' ] not in _VALID_TYPES:
    raise TemplateError( 'unknown $type "{0}" at "{1}"'.format( template[ '$type' ], path or '<root>' ) )

  if '$match' in template:
    try:
      re.compile( template[ '$match' ] )
    except re.error as e:
      raise TemplateError( 'invalid $match pattern at "{0}": {1}'.format( path or '<root>', e ) )

  if '$loose' in template and not isinstance( template[ '$loose' ], bool ):
    raise TemplateError( '$loose at "{0}" must be a bool'.format( path or '<root>' ) )

  if '$in' in template:
    if not isinstance( template[ '$in' ], list ) or not template[ '$in' ]:
      raise TemplateError( '$in at "{0}" must be a non-empty list'.format( path or '<root>' ) )

  if '$each' in template:
    checkTemplate( template[ '$each' ], _join( path, '[]' ) )

  if '$or' in template:
    alternatives = template[ '$or' ]

    if not isinstance( alternatives, list ) or not alternatives:
      raise TemplateError( '$or at "{0}" must be a non-empty list'.format( path or '<root>' ) )

    for index, alternative in enumerate( alternatives ):
      checkTemplate( alternative, _join( path, '$or[{0}]'.format( index ) ) )

  if '$contains' in template:
    contains = template[ '$contains' ]

    if isinstance( contains, list ):
      if '$contains_count' in template:
        raise TemplateError( '$contains_count at "{0}" can not be used when $contains is a list of clauses -- put $count on each clause instead'.format( path or '<root>' ) )

      if not contains:
        raise TemplateError( '$contains at "{0}" must not be an empty list'.format( path or '<root>' ) )

      for index, clause in enumerate( contains ):
        clause_path = _join( path, '$contains[{0}]'.format( index ) )

        if not isinstance( clause, dict ) or '$template' not in clause:
          raise TemplateError( '$contains clause at "{0}" must be a dict with a "$template" key'.format( clause_path ) )

        if set( clause ) - { '$template', '$count' }:
          raise TemplateError( '$contains clause at "{0}" must only contain $template/$count'.format( clause_path ) )

        checkTemplate( clause[ '$template' ], clause_path )

        if '$count' in clause:
          _checkCountSpec( clause[ '$count' ], '$count', clause_path )

    else:
      checkTemplate( contains, _join( path, '$contains' ) )

  if '$count' in template:
    _checkCountSpec( template[ '$count' ], '$count', path )

  if '$contains_count' in template:
    _checkCountSpec( template[ '$contains_count' ], '$contains_count', path )

  for key, value in template.items():
    if isinstance( key, str ) and key.startswith( '$' ):
      continue

    checkTemplate( value, _join( path, key ) )
