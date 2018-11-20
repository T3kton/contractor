Basic install
=============

Building
--------

Building requires running on a Ubuntu Xenial machine.

Create an empty directory, and cd into it

first clone the contractor and related projects::

  git clone https://github.com/T3kton/contractor.git
  git clone https://github.com/T3kton/contractor_plugins.git
  git clone https://github.com/T3kton/subcontractor.git
  git clone https://github.com/T3kton/subcontractor_plugins.git
  git clone https://github.com/T3kton/resources.git

install the required build tools, the PPA has a few required packages for building
and installing::

  add-apt-repository ppa:pnhowe/t3kton
  apt update
  apt install respkg build-essential dpkg-dev debhelper python3-dev python3-setuptools nodejs npm nodejs-legacy liblzma-dev

now to build Contractor, first we need to get the node requirements for the UI, and fix a bug with react-toolbox::

  cd contractor
  cd ui && npm install
  sed s/"export Ripple from './tooltip';"/export { default as Ripple } from './ripple';/ -i ui/node_modules/react-toolbox/components/index.js
  sed s/"export Tooltip from './tooltip';"/export { default as Tooltip } from './tooltip';/ -i ui/node_modules/react-toolbox/components/index.js
  make
  make dpkg
  make respkg
  mv *.respkg ..
  cd ..

now to build the others::

  for i in subcontractor contractor_plugins subcontractor_plugins; do cd $i && make dpkg && cd ..; done

and build the resources, the make in the resources can take a while, you may want to add `-j4`( replace the 4 with the number of compile process to parralaize)::

  cd contractor_plugins
  make respkg
  mv *.respkg ..
  cd ../resources
  make respkg
  mv *.respkg ..
  cd ..

Setting Up
----------

create an ubuntu xenial VM, name it "contractor", set the fqdn to "contractor.site1.local"
Ideally it should be in a /24 network.  Ip addresses offsets from 2 to 20 will be
set as reserved (so that contractor will not auto asign them) and offsets 21 - 29
will be used for a dynamic DHCP pool. And off set 1 is assumed to te be the gateway.
All these values can be adjusted either in the setupWizzard file before it is run,
or after it setup, you can use the API/UI to edit these values.
The DNS setver will be set for the contractor VM, and bind on the contractor vm will
be set to forward to the DNS server that was origionally configured on the VM.

The default when installing from package is to use postgres for the database.
sqlite is also supported, and the prefered way for developmnet.  You can edit the
/etc/contractor/master.conf to enable the sqlite option if desired.  Keep in mind
that sqlite option requires making the database writeable by www-data.www-data.

copy the .deb and .respkg files from the build server to the new contractor vm.

setup repos and install some required tools::

  add-apt-repository ppa:pnhowe/t3kton
  apt update
  apt install bind9 postgresql-9.5

Install Packages::

  dpkg -i contractor_0*.deb subcontractor_0*.deb contractor-plugins_0*.deb subcontractor-plugins_0*.deb
  apt install -f

Create the postgres db::

  su postgres -c "echo \"CREATE ROLE contractor WITH PASSWORD 'contractor' NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN;\" | psql"
  su postgres -c "createdb -O contractor contractor"

NOTE: setupWizzard is going to re-write some bind config files, so don't edit them.  Until after, if needed.

the ubuntu toml package is to old::

  apt install python3-pip
  pip3 install toml --upgrade

Now to create the db::

  /usr/lib/contractor/util/manage.py migrate

Install base os config::

  respkg -i contractor-os-base_0.0.respkg

Now to enable plugins::

  respkg contractor-plugins-manual

if you are using vcenter::

  respkg contractor-plugins-vcenter

if you are using virtualbox::

  respkg contractor-plugins-virtualbox

do manual plugin again so it can cross link to the other plugins::

  respkg contractor-plugins-manual

Now to setup some base info, and configure bind::

  /usr/lib/contractor/setup/setupWizzard

Restart bind with new zones::

  service bind9 restart

This VM needs to use the contractor generated dns, so edit
/etc/network/interfaces to set the dns server to 127.0.0.1
then, reload networking configuration::

  systemctl restart networking

Now to disable the extra apache site::

  a2dissite 000-default
  service apache2 reload

yon now take a look at the contractor ui at http://<contractor ip>

now we will install subcontractor::

  apt install subcontractor subcontractor-plugins tftpd-hpa
  respkg contractor-ipxe

now edit /etc/subcontractor.conf
enable the modules you want to use, remove the ';' and set the 0 to a 1.
The 1 means one task for that plugin at a time, if you want things to go faster,
you can try 2 or 4.  Depending on the plugin, the resources of your vm, etc.

edit /etc/subcontractor.conf in the dhcpd section, make sure interface and tftp_server
are correct, tftp_server should be the ip of the vm

now start up subcontractor::

  systemctl start subcontractor
  systemctl start dhcpd

make sure it's running::

  systemctl status subcontractor
  systemctl status dhcpd

optional, edit /etc/default/tftpd-hpa and add '-v ' to TFTP_OPTIONS.  This will
cause tfptd to log transfers to syslog.  This can be helpfull in troubleshooting
boot problems. Make sure to run `service tftpd-hpa restart` to reload.

edit /etc/apache2/sites-available/contractor.conf

/etc/apache2/sites-available/static.conf::

  <VirtualHost *:80>
    ServerName static
    ServerAlias static.<domain>

    DocumentRoot /var/www/static

    LogFormat "%a %t %D \"%r\" %>s %I %O \"%{Referer}i\" \"%{User-Agent}i\" %X" static_log
    ErrorLog ${APACHE_LOG_DIR}/static_error.log
    CustomLog ${APACHE_LOG_DIR}/static_access.log static_log
  </VirtualHost>
