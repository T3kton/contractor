WARNING!!! this is not workable yet, hopfully soon.

Contractor
==========

Overview
--------

Contractor is a builder of anything, and is targeted to be used as a generic API
to create/destroy/manipluate your resources no matter where or what they are.
This enables you to focus on what you want to make, and not have to worry about
the details and differences in deployment.

To acomplish this, Contractor breaks the deployment/provisioning step into two parts.  A
Structure, or what it is you want to deploy, and a Foundation, or what you want
to deploy it on.  Examples of Foundations are VirtualBox VMs, Docker Containers,
Servers with IPMI, Servers with out out-of-band controll, Switches, PDUs, AWS, GCD,
or just about anything else.  A Structure would be a DNS server, API Endpoint,
Load Balanacer, Web Server, Docker Host, VirtualBox Host, CoreOS Server, etc.  To
describe a Structure, a BluePrint is used.  A BluePrint provides the configuration
information needed to create the Structure.  There are also BluePrints for Foundations,
which describe firmwares, machine level configuration (ie: IPMI configuration ), as
well as contain information to fingerprint foundations, for example a Foundation
BluePrint can require a certin number of CPUs and Memory, PCI devices, as well
as storage details.  Each Structure and Foundation belong to a grouping called
a Site.  Sites can belong to other Sites, and a Structure does not need to belong
to the same Site as its foundation.  The Site can also contain configuration
information that the Structures and Foundations that belong to it inherit.
This way a configuration such as DNS Server can be maintained at the Site level
and automatically propagate to everything inside that Site.

At its core Contractor has a scripting language called TScript.  Each BluePrint
has a Create and Destroy script that is executed to create and destroy that Structure
or in the case of Foundations, provision and deprovision.  Utility scripts can also
be created, for example, if a new firmware for a storage controller is released.
A utility script can be created to deploy this new firmware, and a Job can be created
to execute the script.  Jobs are run by the Foreman subsystem.  When a new Foundation
has been detected, or a Structure's Foundation has been provisioned, Foreman will
provide instructions to a SubContractor daemon to do indivitual required tasks 
for that Foundation to be Provisioned or Structure to be created.

SubContractor is a daemon that is run in appropriate parts of the network for
handeling tasks as requested by the Script being executed in the Job.  All tasks
are asked for by SubContracor, over HTTP (fully proxyable) thus Contractor itsself
does not have to have access to sensitive parts of the network, it only
needs to be visiable to SubContractor.  Each SubContractor can be configured to
only do certian types of work.  For example a SubContractor can be configured to
do only IPMI tasks enabeling the IPMI network to be isolated from other networks.
Other SubContractors can then handel PXE booting the servers and perform other checks
such as checking to see if port 22 is open (a common and easy way to make sure
a Structure with SSH installed has sucessfully booted).


Future
------
Contractor being able to build everything can also be used as a single source of
truth.  Thus providing a place where you can ask questions such as "How many Load
Ballancers do we have", "What Services will taking this host down affect", or
"How many VM resources are being used to support this service".  Contractor has a
Bind zone file generating ability that can be used to maintain DNS records, which
will automatially update when things are added/removed.  With Contractor you do
not have to wait for a new VM to register with a service.  That Service can query
Contractor to know what should be  registered with it, and act if a registered
resource is not connected.  Contractor will also  have webhooks, so services can
be notified on Creation/Destruction events or even hardware events, thus allowing
a service to be able to ask for a harddrive replacment to wait until it is able
to take that harddrive out of service nicely.


Installation
------------

After installing the python source, you need to setup the database.  First setup
the DATABASE section of the settings.py file.  See
https://docs.djangoproject.com/en/1.8/ref/settings/#databases for documentation
on database setup.  The settings.py file is preconfigured to use  sqlite and store
the database in parent directory of the settings.py file.  After the database
connection is setup, create the the database::

  cd /usr/lib/contractor/util
  ./manage.py migrate

to start the API server::

  cd /usr/lib/contractor/api_server
  ./api_server.py


Modules
=======

BluePrint
---------

Containes BluePrint a generic base class for StructureBluePrint and FoundationBluePrint.
Also contains the Scripts and linckages between the BluePrints and Scripts.  And
PXE, things to which PXE bootable devices can be set to boot to.

Building
--------

Contains Foundation a generic base class for all Foundations provided by plugins.
Structure the class for Structures that go on Foundations.  Complex, a
grouping of Foundations (ie: a cluster).  Dependancy, allows Foundations to
depend on Structures and/or jobs to be complete on a structure.

Foreman
-------

Contains BaseJob a generic base class for FoundationJob, StructureJob and DependancyJob,
which are jobs that are inflight for Foundations, Structures, and Dependancies
respectivly.

Site
----

Contains Site, for grouping Foundations and Structurres into logical groups for
easier managment.

SubContractor
-------------

interface for subcontractor, probably going to get moved to Foreman

User
----

Handels Contractor Users.

Utilities
---------

Handels Network Interfaces, Ip Addresses, and Power interfaces (Not  all flushed out yet)


lib
---

Common utilties for all of  Contractor

tscript
-------

T3kton Script parser and runner
