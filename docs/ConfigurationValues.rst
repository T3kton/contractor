Configuration Values
====================

config value key names must match the regex::

  ^[{}\-~]?([a-zA-Z0-9]+:)?[a-zA-Z0-9][a-zA-Z0-9_\-]*$

if the first charater is: (also processed in this order)
  - : remove from the value so far
  <nothing> : overlay/replace value so far with new value
  { : prepend to the value so far (same affect as append on dict/maps)
  } : append to the value so far
  ~ : mask/remove value so far, (NOTE: value is ignored)

if [a-zA-Z0-9]+: is present, the value key/value is only applied if the pre ':'
matches the classes indicated by the foundation.  This is the **_foundation_class_list**


Value Overlay Rules
-------------------

For Site and BluePrint, the values of the parents are overlied by the children.


Sources of Configuraion Values
------------------------------

Foundation does not it's self have values, however attributes of the foundation,


For a Site
 Parents in order from parent to child
 Global attribute values

For a Foundation
  Site (with it's parents applied)
  Complex attribute values if Foundation belongs to a complex
  Foundation's BluePrint (with it's parents applied)
  Foundation's attribute values
  Global attribute values

For a Structure
  Site (with it's parents applied)
  Structures's BluePrint (with it's parents applied)
  Foundation's attribute values  NOTE: the  Foundation's BluePrint values are NOT
                                       used, these are only for the physicall
                                       provisioning of the Foundation, ie: BIOS
                                       settings, the Structure can specify values
                                       for the Foundation by which
                                       FoundationBluePrints the Structure
                                       BluePrint supports
  Structure's config_values
  Structure's attribute values
  Global attribute values


Attribute Values
----------------

These values start with `_` and are not  overlayable/modifyable by config_Values.
These values are attributes of the structure/foundation/complex, such as the
structure/foundation/complex id, `_structure_config_uuid`, `_structure_hostname`,
structure/foundation/complex state.


Global attribute values
-----------------------

These values start with `__` and are not overlayable/modifyable by config_values.  These
values are things that are global to this install of contrator,  such as the base url
to use to contact it.  `__last_modified` is also added, which is the timestamp of
the most reset modification date to any of the sources of configuratoin information.
