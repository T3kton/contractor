# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import contractor.fields


def load_generic_pxe( app, schema_editor ):
  PXE = app.get_model( 'BluePrint', 'PXE' )

  pxe = PXE( name='normal-boot' )
  pxe.boot_script = """echo Booting form Primary Boot Disk
sanboot --no-describe --drive 0x80 || echo Primary Boot Disk is not Bootable"""
  pxe.template = ''
  pxe.save()


def load_linux_blueprints( app, schema_editor ):
  StructureBluePrint = app.get_model( 'BluePrint', 'StructureBluePrint' )
  Script = app.get_model( 'BluePrint', 'Script' )
  BluePrintScript = app.get_model( 'BluePrint', 'BluePrintScript' )
  PXE = app.get_model( 'BluePrint', 'PXE' )

  sbpm = StructureBluePrint( name='generic-manual-structure', description='Manual OS' )
  sbpm.full_clean()
  sbpm.save()

  s = Script( name='create-manual-structure', description='Install Manual OS' )
  s.script = """# Install Manual OS
pause( msg='Resume When OS is Installed' )
pause( msg='Resume When OS has been verified to be running' )
"""
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=sbpm, script=s, name='create' ).save()

  s = Script( name='destroy-manual-structure', description='Uninstall Manual OS' )
  s.script = """# Uninstall Manual OS
pause( msg='Resume When OS is Uninstalled' )
"""
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=sbpm, script=s, name='destroy' ).save()

  s = Script( name='utility-manual-structure', description='Utility Script for Manual OS' )
  s.script = """# Utility Script for Manual OS
pause( msg='Do the thing, then Resume' )
"""
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=sbpm, script=s, name='utility' ).save()

  sbpl = StructureBluePrint( name='generic-linux', description='Generic Linux' )
  sbpl.config_values = { 'distro': 'generic' }
  sbpl.full_clean()
  sbpl.save()

  sbpu = StructureBluePrint( name='generic-ubuntu', description='Generic Ubuntu' )
  sbpu.config_values = { 'distro': 'ubuntu' }
  sbpu.parent = sbpl
  sbpu.full_clean()
  sbpu.save()

  sbpx = StructureBluePrint( name='generic-xenial', description='Generic Ubuntu Xenial (16.04 LTS)' )
  sbpx.config_values = { 'distro_version': 'xenial', 'awsec2_image_id': 'ami-efd0428f', 'docker_image': 'xenial/ssh' }
  sbpx.parent = sbpu
  sbpx.full_clean()
  sbpx.save()

  s = Script( name='create-linux', description='Install Linux' )
  s.script = """# pxe boot and install
ssh_port = 22

if ( foundation.type == "AWSEC2" ) then
begin( description="Provision AWS EC2" )
  # should allready be ready to go and started
end
elif ( foundation.type == "Docker" ) then
begin( description="Provision Docker" )
  ssh_port = 4222
  foundation.start()
end
else
begin( description="Provision From Installer" )
  if not structure.provisioning_interface then
    fatal_error( msg="Provisioning Interface Not Defined" )

  dhcp.set_pxe( interface=structure.provisioning_interface, pxe="ubuntu" )
  foundation.power_on()
  delay( seconds=120 )
  foundation.wait_for_poweroff()

  dhcp.set_pxe( interface=structure.provisioning_interface, pxe="normal-boot" )
  foundation.power_on()
end

begin( description="Verify Running" )
  iputils.wait_for_port( target=structure.provisioning_ip, port=ssh_port )
end
"""
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=sbpl, script=s, name='create' ).save()

  s = Script( name='destroy-linux', description='Uninstall Linux' )
  s.script = """# nothing to do, foundation cleanup should wipe/destroy the disks
foundation.power_off()
#eventually pxe boot to MBR wipper
"""
  s.full_clean()
  s.save()
  BluePrintScript( blueprint=sbpl, script=s, name='destroy' ).save()

  pxe = PXE( name='ubuntu' )
  pxe.boot_script = """echo Ubuntu Installer
kernel tftp://192.168.200.10/ubuntu/vmlinuz auto url=http://192.168.200.1:8888/config/pxe_template/ locale=en_US.UTF-8 keyboard-configuration/layoutcode=us domain=example.com hostname={{ hostname }}
initrd tftp://192.168.200.10/ubuntu/initrd
boot
"""
  pxe.template = """
d-i debian-installer/locale string en_US
d-i console-setup/ask_detect boolean false
d-i keyboard-configuration/xkb-keymap select us

d-i netcfg/choose_interface select auto

# If you prefer to configure the network manually, uncomment this line and
# the static network configuration below.
#d-i netcfg/disable_autoconfig boolean true

# Static network configuration.
#
# IPv4 example
#d-i netcfg/get_ipaddress string 192.168.1.42
#d-i netcfg/get_netmask string 255.255.255.0
#d-i netcfg/get_gateway string 192.168.1.1
#d-i netcfg/get_nameservers string 192.168.1.1
#d-i netcfg/confirm_static boolean true

d-i netcfg/hostname string {{ hostname }}

### Mirror settings
d-i mirror/country string manual
d-i mirror/http/hostname string mirror.mozy.com
d-i mirror/http/directory string /ubuntu
d-i mirror/http/proxy string http://192.168.200.10:3128/

# Suite to install.
d-i mirror/suite string xenial

### Account setup
d-i passwd/make-user boolean false
d-i user-setup/allow-password-weak boolean true
d-i passwd/root-login boolean true
d-i passwd/root-password password r00tme
d-i passwd/root-password-again password r00tme
d-i user-setup/encrypt-home boolean false

### Clock and time zone setup
d-i clock-setup/utc boolean true
d-i time/zone string UTC

# Controls whether to use NTP to set the clock during the install
d-i clock-setup/ntp boolean true
d-i clock-setup/ntp-server string ntp.ubuntu.com

### Partitioning
## Partitioning example
d-i partman-auto/disk string /dev/sda
d-i partman-auto/method string regular
d-i partman-lvm/device_remove_lvm boolean true
d-i partman-md/device_remove_md boolean true
d-i partman-lvm/confirm boolean true
d-i partman-lvm/confirm_nooverwrite boolean true
d-i partman-auto/choose_recipe select atomic
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true

d-i partman/mount_style select uuid

### Base system installation
#d-i base-installer/install-recommends boolean false
#d-i base-installer/kernel/image string linux-generic

### Package selection
tasksel tasksel/first multiselect server

d-i pkgsel/include string openssh-server
d-i pkgsel/upgrade select safe-upgrade
d-i pkgsel/update-policy select none

popularity-contest popularity-contest/participate boolean false

### Boot loader installation
d-i grub-installer/only_debian boolean true
d-i grub-installer/with_other_os boolean true
d-i grub-installer/bootdev  string /dev/sda

### Finishing up the installation
d-i finish-install/reboot_in_progress note
d-i debian-installer/exit/poweroff boolean true

"""
  pxe.save()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrint',
            fields=[
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('config_values', contractor.fields.MapField(blank=True, default={})),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BluePrintScript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PXE',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('boot_script', models.TextField()),
                ('template', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('name', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('script', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FoundationBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, to='BluePrint.BluePrint', serialize=False)),
                ('foundation_type_list', contractor.fields.StringListField(max_length=200, default=[])),
                ('template', contractor.fields.JSONField(default={}, blank=True)),
                ('physical_interface_names', contractor.fields.StringListField(max_length=200, default=[], blank=True)),
                ('parent', models.ForeignKey(blank=True, null=True, to='BluePrint.FoundationBluePrint')),
            ],
            bases=('BluePrint.blueprint',),
        ),
        migrations.CreateModel(
            name='StructureBluePrint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, to='BluePrint.BluePrint', serialize=False)),
                ('foundation_blueprint_list', models.ManyToManyField(to='BluePrint.FoundationBluePrint')),
                ('parent', models.ForeignKey(blank=True, null=True, to='BluePrint.StructureBluePrint')),
            ],
            bases=('BluePrint.blueprint',),
        ),
        migrations.AddField(
            model_name='blueprintscript',
            name='blueprint',
            field=models.ForeignKey(to='BluePrint.BluePrint'),
        ),
        migrations.AddField(
            model_name='blueprintscript',
            name='script',
            field=models.ForeignKey(to='BluePrint.Script'),
        ),
        migrations.AddField(
            model_name='blueprint',
            name='scripts',
            field=models.ManyToManyField(to='BluePrint.Script', through='BluePrint.BluePrintScript'),
        ),
        migrations.AlterUniqueTogether(
            name='blueprintscript',
            unique_together=set([('blueprint', 'name')]),
        ),
        migrations.RunPython( load_generic_pxe ),
        migrations.RunPython( load_linux_blueprints ),
    ]
