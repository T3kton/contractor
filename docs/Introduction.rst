Introduction to Contractor
==========================

The Goal of Contractor is to provide a Universial Interface/API to Automate
Mangment, Provisioning, Deploying, and Configuration of Resource.

Contractor uses building terms (for the most part) to try to avoid name
colisions with various platforms and systems.

First two terms are **Foundation** and **Structure**.  A Foundation is something
to build on, a structure is that things you want to  build.  Say we want to
build a Web Server.  Our Structure is a set of configuration values and scripts
required to build that web server, ie: Install Ubuntu LTS 18.04 and install and
Configure Apache (more on thoes deatils in .....).  The Foundation is what we
want to install that on, ie: a VM, Container, Blade Server, Baremetal Server,
Rasbery PI, ECS, GCD, etc...  Not all Foundations are going to be compatiable
with all Structures, however a well defined Structure can be installed on most
of them.

So far we have this::

  +-----------------------------+
  |                             |
  |  Structure (Web Server)     |
  |                             |
  +-----------------------------+
               |
               |
  +-----------------------------+
  |                             |
  |   Foundation                |
  |                             |
  +-----------------------------+


The next term is **Site**.  A site is a Logical grouping of things.  Let's put
our Web Server in a Site called "Cluster 1"

::

  +-------------------------------------+
  |  Cluster 1                          |
  |                                     |
  |    +-----------------------------+  |
  |    |                             |  |
  |    |  Structure (Web Server)     |  |
  |    |                             |  |
  |    +------------+----------------+  |
  |                 |                   |
  |                 |                   |
  |    +------------+----------------+  |
  |    |                             |  |
  |    |   Foundation                |  |
  |    |                             |  |
  |    +-----------------------------+  |
  |                                     |
  +-------------------------------------+

Each Item we have used so far containes configuration values.  These are Key
Value pairs that can be overlayed.  In this case Contractor will take the
configuration values of "Cluster 1" then over lay them with "Foundation" and
the "Structure".

Sites can be be put into other Sites.  For example we have Clusters 1, 2, and 3
in "Datacenter West".

::

  +---------------------------------------------------------------------------------------------+
  | Datacenter West                                                                             |
  |                                                                                             |
  |  +-------------------------------------+ +----------------------+ +----------------------+  |
  |  |  Cluster 1                          | |  Cluster 2           | |  Cluster 3           |  |
  |  |                                     | |                      | |                      |  |
  |  |    +-----------------------------+  | |    +--------------+  | |    +--------------+  |  |
  |  |    |                             |  | |    |              |  | |    |              |  |  |
  |  |    |  Structure (Web Server)     |  | |    |  Structure   |  | |    |  Structure   |  |  |
  |  |    |                             |  | |    |              |  | |    |              |  |  |
  |  |    +------------+----------------+  | |    +-----+--------+  | |    +-----+--------+  |  |
  |  |                 |                   | |          |           | |          |           |  |
  |  |                 |                   | |          |           | |          |           |  |
  |  |    +------------+----------------+  | |    +-----+--------+  | |    +-----+--------+  |  |
  |  |    |                             |  | |    |              |  | |    |              |  |  |
  |  |    |   Foundation                |  | |    |  Foundation  |  | |    |  Foundation  |  |  |
  |  |    |                             |  | |    |              |  | |    |              |  |  |
  |  |    +-----------------------------+  | |    +--------------+  | |    +--------------+  |  |
  |  |                                     | |                      | |                      |  |
  |  +-------------------------------------+ +----------------------+ +----------------------+  |
  |                                                                                             |
  +---------------------------------------------------------------------------------------------+

Now the configuration information will first have site "Datacenter West" then,
Cluster X, Foundation, Structure.  This comes in handy for propagating configuration
information without having to set it for each item indivitually.  For Example
we can have the DNS Search Zones be set to "west.site.com" in the site "Datacenter West"
and prepend that with "cluster1.site.com" in "Cluster 1".  If at any time we want
some other global DNS search zone, we add it to the top and it automatically propagates
down.   You could also set "Release"="Prod" in "Datacenter West" and then create a
"Cluster Test" and override the "Release" to the value "Test".  You could also do
A-B testing, etc.

Any Item can make a http request to contractor and contractor will reply with a JSON
encoded reply with that items combined configuration values.

This is all fun and all, but not really usefull.  Let's change things up abit and
install ESX on the baremetal and put a few Web servers on ESX.

Before we do that we need to dig into foundations a little more. The **Foundation**
class is meant as a root class for specific target handelers to work against.

We are going to use the **IPMIFoundation** to handle the baremetal machines on which
we are installing ESX on, and **VCenterFoundation** to handle the vms on the
ESX/VCenter.

Note: we are going to omit Cluster 2 and 3 for now, they are clones of Cluster 1::

  +-----------------------------------------------------------------------------+
  | Datacenter West                                                             |
  |                                                                             |
  |  +-----------------------------------------------------------------------+  |
  |  |  Cluster 1                                                            |  |
  |  |                                                                       |  |
  |  |  +-----------------------------+ +-----------------------------+      |  |
  |  |  |                             | |                             |      |  |
  |  |  |  Structure (Web Server)     | |  Structure (Web Server)     |      |  |
  |  |  |                             | |                             |      |  |
  |  |  +------------+----------------+ +------------+----------------+      |  |
  |  |               |                               |                       |  |
  |  |               |                               |                       |  |
  |  |  +------------+----------------+ +------------+----------------+      |  |
  |  |  |                             | |                             |      |  |
  |  |  |   VCenterFoundation         | |   VCenterFoundation         |      |  |
  |  |  |                             | |                             |      |  |
  |  |  +------------------------+----+ +---+-------------------------+      |  |
  |  |                           |          |                                |  |
  |  |                      +----+----------+---+                            |  |
  |  |                      |                   |                            |  |
  |  |                      | VCenter Complex   |                            |  |
  |  |                      |                   |                            |  |
  |  |                      +--------+----------+                            |  |
  |  |                               |                                       |  |
  |  |                  +------------+----------------+                      |  |
  |  |                  |                             |                      |  |
  |  |                  |  Structure (ESX)            |                      |  |
  |  |                  |                             |                      |  |
  |  |                  +------------+----------------+                      |  |
  |  |                               |                                       |  |
  |  |                               |                                       |  |
  |  |                  +------------+----------------+                      |  |
  |  |                  |                             |                      |  |
  |  |                  |   IPMIFoundation            |                      |  |
  |  |                  |                             |                      |  |
  |  |                  +-----------------------------+                      |  |
  |  |                                                                       |  |
  |  +-----------------------------------------------------------------------+  |
  |                                                                             |
  +-----------------------------------------------------------------------------+

This introduces our next item the **Complex** as in a building complex.  A Complex
is a group of structures providing something for more Foundations to be built on.
A Complex (dependingon the type) can have one or more structures as members.
NOTE: the configuration info of the structure and foundations that make up a
cluster do **NOT** flow through to the foundations and structures built on that
complex.  The Members of the Complex can even belong to another site.

For Example::

  +-----------------------------------------------------------------------------+
  | Datacenter West                                                             |
  |                                                                             |
  |  +-----------------------------------------------------------------------+  |
  |  |  Cluster 1                                                            |  |
  |  |                                                                       |  |
  |  |  +-----------------------------+ +-----------------------------+      |  |
  |  |  |                             | |                             |      |  |
  |  |  |  Structure (Web Server)     | |  Structure (Web Server)     |      |  |
  |  |  |                             | |                             |      |  |
  |  |  +------------+----------------+ +------------+----------------+      |  |
  |  |               |                               |                       |  |
  |  |               |                               |                       |  |
  |  |  +------------+----------------+ +------------+----------------+      |  |
  |  |  |                             | |                             |      |  |
  |  |  |   VCenterFoundation         | |   VCenterFoundation         |      |  |
  |  |  |                             | |                             |      |  |
  |  |  +------------------------+----+ +---+-------------------------+      |  |
  |  |                           |          |                                |  |
  |  +-----------------------------------------------------------------------+  |
  |  |                           |          |                                |  |
  |  |  Cluster 1 Hosting   +----+----------+---+                            |  |
  |  |                      |                   |                            |  |
  |  |                      | VCenter Complex   |                            |  |
  |  |                      |                   |                            |  |
  |  |                      +---+-------------+-+                            |  |
  |  |                          |             |                              |  |
  |  |                          |             |                              |  |
  |  |                          |             |                              |  |
  |  |                          |             |                              |  |
  |  |     +--------------------+------+   +--+-------------------------+    |  |
  |  |     |                           |   |                            |    |  |
  |  |     | Structure (ESX)           |   | Structure (ESX)            |    |  |
  |  |     |                           |   |                            |    |  |
  |  |     +----------+----------------+   +-----------+----------------+    |  |
  |  |                |                                |                     |  |
  |  |                |                                |                     |  |
  |  |     +----------+----------------+   +-----------+----------------+    |  |
  |  |     |                           |   |                            |    |  |
  |  |     |  IPMIFoundation           |   |  IPMIFoundation            |    |  |
  |  |     |                           |   |                            |    |  |
  |  |     +---------------------------+   +----------------------------+    |  |
  |  |                                                                       |  |
  |  +-----------------------------------------------------------------------+  |
  |                                                                             |
  +-----------------------------------------------------------------------------+

Complexes also cause Contractor to build the Web Server Structure/Foundations
after the ESX Structure/Foundations are done.  Also the exmaple would look pretty
much the same for a Docker/OpenStack/etc Complex.

Side Track to the Manefesto
---------------------------

At this point you are probably wondering how having all these Foundation types
is simplifying deployments.  By Seperating the configuration of the "Hosted" and
the "Host" we can effectivly divide up the job of configuraing the sytem.  (Do
I get to drop the DevOps Buzzword now?)  As a Developer/Enginner configures their
code, the embody that in a structure.  They can package that configuration
information along with their code/designs and that configuration can also
be tested and verified via CICD and simmaler work flows.  This way the very
same configuration information is for all stages of deployment.  It is true
that some foundations require different considerations, however a well designed
Structure Configuration can work for Containers (and the like) as well as
OS installes (Baremetal/VM/Blade/AWS, etc.)  Now we the Operations people need to
turn it up to 11 (or 12) they just pick the location to deploy and no matter if
it is hosted on prem in VMs, or deployed to AWS for some peak load handeling,
Operations can scale as needed, to what ever.

Also by allowing every thing, no matter the platform, to be tracked in the same
place.  You now have a single source of truth for your monitoring sytem to rely on.
And you don't have to worry about parts of your Micro Services failing to auto-register.
And you know exactly what is deployed where, usefull when hardware needs to be
swapped out.

Your Operations teams are also free to try changing out hosting solutions without
retooling everything to try it.  And in some cases without involving Enginerring
to do so.

Not only can you unify your provivsioning tools, but also the auto-scaling tools.

You are also free from vendor lock in.  If a new Cloud provier comes along, they
don't need to have a AWS like API to use them, just a Foundation subclass
provider that talks to that Cloud provider's API and you are set.  Same if
a new class of hardware comes along (ARM servers anyone ;-) ) or a new way of
approcing hosting (the next thing after containers).  You can truly be
"serverless" (I know another buzzword, meaning your deyployments are agnostic
as to the techonlogy they are being deployed on).  And you don't have to try to
fit all your use cases into one silver bullet.  You can have a nice auto-scaling
Container Cloud/Swarm with your micro services right next to standard VMs running
the databases and object storage.  All with one "pane of glass"

Ok back to business, buzzword dropping disabled...

Back to business
----------------

One final piece of the deployment puzzle, the **Dependancy**.  This is to make sure
your deployments happen in order.  For example, you can't install any OSes untill
the Switch is provisioned.  Also you may have to allocate space on a NFS mount
before installing a VM.  This is where Dependancies come in, allowing a Foundation
to Depend on a Structure being build, and/or a job being run on a Structure.


BluePrints
----------

Now that we have talked about the parts, we need to talk about how thoes things
are confugred and that is handled by **BluePrint**, specifially the
**FoundationBluePrint** and the **StructureBluePrint**.  A Blueprint also holds
cocnfiguration values, as well as links to scripts which are executed when the
Structure/Foundation that blueprint is for is configured, destroyed, or had a named
script run on it.  The BluePrint is the thing that Engineering and Operations
build to embody the process and configuration information of Creating the
Structure/Foundation.

Other
-----

There are other Classes/Components in Contractor, but they are mostlly for dealing
with Configure/Destroy/Misc Jobs (the Formen module).  As well as keeping track
of Ip Addresses and other "Utilities".  Thoes are documented else where.
