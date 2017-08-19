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


Example
-------

NOTE: for the following examples the ip address attributes and global attributes
are ommited.

Let's start with a Site with the following values::

  +-------------------------------------------+
  |                                           |
  | dns_servers: [ '10.0.0.20', '10.0.0.21' ] |
  | dns_search: [ 'myservice.com' ]           |
  | dns_zone: 'myservice.com'                 |
  |                                           |
  +-------------------------------------------+

Nice and simple.  This Example is mostly going to deal with dns, but the
config vaules can be  used for just about anything.

Let's add a Foundation and Structure (NOTE: the Foundation and Structure
provide more attribute values than what is shown)::

  +-------------------------------------------+
  |                                           |
  | dns_servers: [ '10.0.0.20', '10.0.0.21' ] |
  | dns_search: [ 'myservice.com' ]           |
  | dns_zone: 'myservice.com'                 |
  |                                           |
  | +----------------------+                  |
  | |                      |                  |
  | | Structure:           |                  |
  | |   Hostname: web1     |                  |
  | |                      |                  |
  | +----------+-----------+                  |
  |            |                              |
  | +----------+-----------+                  |
  | |                      |                  |
  | | Foundation:          |                  |
  | |   Locater: d2r050u20 |                  |
  | |                      |                  |
  | +----------------------+                  |
  |                                           |
  +-------------------------------------------+

Now if we get the config values for the structure, it's resulting config values
would be.

  dns_servers: [ '10.0.0.20', '10.0.0.21' ]
  dns_search: [ 'myservice.com' ]
  dns_zone: 'myservice.com'
  _foundation_locator: 'd2r050u20'
  _structure_hostname: 'web1'

One last thing we forgot, the blueprints::

  +-------------------------------------------+
  |                                           |
  | dns_servers: [ '10.0.0.20', '10.0.0.21' ] |
  | dns_search: [ 'myservice.com' ]           |
  | dns_zone: 'myservice.com'                 |    +----------------------------------------------------------------------+
  |                                           |    |                                                                      |
  | +----------------------+                  |    | Web Server Structure BluePrint:                                      |
  | |                      +-----------------------+   distro: 'xenial'                                                   |
  | | Structure:           |                  |    |   extra_packages: [ 'apache2', 'python-django', 'postgres-server' ]  |
  | |   Hostname: 'web1'   |                  |    |                                                                      |
  | |                      |                  |    +----------------------------------------------------------------------+
  | +----------+-----------+                  |
  |            |                              |    +----------------------------------------------------------------------+
  | +----------+-------------+                |    |                                                                      |
  | |                        +---------------------+ Small VM Foundation BluePrint:                                       |
  | | Foundation:            |                |    |   cpu_count: 2                                                       |
  | |   Locater: 'd2r050u20' |                |    |   memory: 1024                                                       |
  | |                        |                |    |                                                                      |
  | +------------------------+                |    +----------------------------------------------------------------------+
  |                                           |
  +-------------------------------------------+

There we go, now the Structures Config Values are::

  dns_servers: [ '10.0.0.20', '10.0.0.21' ]
  dns_search: [ 'myservice.com' ]
  dns_zone: 'myservice.com'
  distro: 'xenial'
  extra_packages: [ 'apache2', 'python-django', 'postgres-server' ]
  _foundation_locator: 'd2r050u20'
  _structure_hostname: 'web1'

And the Foundation's Config Values are::

  dns_servers: [ '10.0.0.20', '10.0.0.21' ]
  dns_search: [ 'myservice.com' ]
  dns_zone: 'myservice.com'
  cou_count: 2
  memory: 1024
  _foundation_locator: 'd2r050u20'

Everythnig was fine till our web site got busy, time to expand.  First let's
move our server to a sub-site and create another sub-site with it's own
web server::

  +----------------------------------------------------------------------------------------------+
  |                                                                                              |
  | dns_servers: [ '10.0.0.20', '10.0.0.21' ]                                                    |
  | dns_search: [ 'myservice.com' ]                                                              |
  | dns_zone: 'myservice.com'                                                                    |
  |                                                                                              |
  | +-------------------------------------------+  +-------------------------------------------+ |
  | |                                           |  |                                           | |
  | | {dns_search: [ 'site1.myservice.com' ]    |  | {dns_search: [ 'site2.myservice.com' ]    | |
  | | dns_zone: 'site1.myservice.com            |  | dns_zone: 'site2.myservice.com            | |   +----------------------------------------------------------------------+
  | |                                           |  |                                           | |   |                                                                      |
  | | +----------------------+                  |  | +----------------------+                  | |   | Web Server Structure BluePrint:                                      |
  | | |                      +-----------------------+                      +------------------------+   distro: 'xenial'                                                   |
  | | | Structure:           |                  |  | | Structure:           |                  | |   |   extra_packages: [ 'apache2', 'python-django', 'postgres-server' ]  |
  | | |   Hostname: 'web1'   |                  |  | |   Hostname: 'web1'   |                  | |   |                                                                      |
  | | |                      |                  |  | |                      |                  | |   +----------------------------------------------------------------------+
  | | +----------+-----------+                  |  | +----------+-----------+                  | |
  | |            |                              |  |            |                              | |   +----------------------------------------------------------------------+
  | | +----------+-------------+                |  | +----------+-------------+                | |   |                                                                      |
  | | |                        +---------------------+                        +----------------------+ Small VM Foundation BluePrint:                                       |
  | | | Foundation:            |                |  | | Foundation:            |                | |   |   cpu_count: 2                                                       |
  | | |   Locater: 'd2r050u20' |                |  | |   Locater: 'd2r020u20' |                | |   |   memory: 1024                                                       |
  | | |                        |                |  | |                        |                | |   |                                                                      |
  | | +------------------------+                |  | +------------------------+                | |   +----------------------------------------------------------------------+
  | |                                           |  |                                           | |
  | +-------------------------------------------+  +-------------------------------------------+ |
  |                                                                                              |
  +----------------------------------------------------------------------------------------------+

Nice, now we can handle the load.  Site 1's Structure is now::

  dns_servers: [ '10.0.0.20', '10.0.0.21' ]
  dns_search: [ 'site1.myservice.com', 'myservice.com' ]
  dns_zone: 'site1.myservice.com'
  distro: 'xenial'
  extra_packages: [ 'apache2', 'python-django', 'postgres-server' ]
  _foundation_locator: 'd2r050u20'
  _structure_hostname: 'web1'

And Site 2's Structure is::

  dns_servers: [ '10.0.0.20', '10.0.0.21' ]
  dns_search: [ 'site2.myservice.com', 'myservice.com' ]
  dns_zone: 'site2.myservice.com'
  distro: 'xenial'
  extra_packages: [ 'apache2', 'python-django', 'postgres-server' ]
  _foundation_locator: 'd2r020u20'
  _structure_hostname: 'web1'

At some point in the future we add another DNS server, we can add it to the top
level and it will propagate to everything automatically.  Actually a better DNS
design would be to add dns servers to site1 and site 2 and prepend thoes to the
dns server list.  Also if we want another global dns search zone to come after
'myservice.com', we can add it to the list at the top, and once again.  It will
Propagate for us.  If there is a site that you do not want to  inherit the
top level dns_search, you  would omit the **{** from the name, and the value will
overwrite instead of pre-pend
