#!/usr/bin/python3
#
# TODO: windows network- and disk-driver not virtio
#

import os
import sys
import json


def diskimages_get(hostdata, tempdir):
	diskimages = {}
	if "image" in hostdata:
		dn = 0
		for disk in hostdata["disks"]:
			if dn == 0:
				imgname = hostdata["image"].split("/")[-1]
				diskimages[disk] = "libvirt/images/" + hostdata["hostname"] + "_" + disk + "_" + imgname
			else:
				diskimages[disk] = "libvirt/images/" + hostdata["hostname"] + "_" + disk + ".qcow2"
			dn += 1
	else:
		for disk in hostdata["disks"]:
			diskimages[disk] = "libvirt/images/" + hostdata["hostname"] + "_" + disk + ".qcow2"
	return diskimages


def diskimages_create(hostdata, tempdir):
	print(" generate diskimages")
	diskimages = diskimages_get(hostdata, tempdir)
	if "image" in hostdata:
		dn = 0
		for disk in diskimages:
			if not os.path.exists(diskimages[disk]):
				if dn == 0:
					print("  generate diskimages: " + diskimages[disk])
					os.system("cp '" + hostdata["image"] + "' '" + diskimages[disk] + "'")
				else:
					print("  " + diskimages[disk] + " (" + hostdata["disks"][disk]["size"] + ")")
					os.system("qemu-img create -f qcow2 '" + diskimages[disk] + "' " + hostdata["disks"][disk]["size"] + " >/dev/null")
			dn += 1
	else:
		for disk in diskimages:
			if not os.path.exists(diskimages[disk]):
				print("  " + diskimages[disk] + " (" + hostdata["disks"][disk]["size"] + ")")
				os.system("qemu-img create -f qcow2 '" + diskimages[disk] + "' " + hostdata["disks"][disk]["size"] + " >/dev/null")
				if hostdata["os"] == "osx___________________":
					os.system("modprobe nbd max_part=8")
					os.system("qemu-nbd --connect=/dev/nbd0 '" + diskimages[disk] + "'")
					os.system("parted /dev/nbd0 --script mklabel gpt")
					os.system("parted /dev/nbd0 --script mkpart primary fat32 40s 409639s")
					os.system("parted /dev/nbd0 --script set 1 esp on")
					os.system("parted /dev/nbd0 --script mkpart primary hfs+ 409640s 100%")
					os.system("fdisk -l /dev/nbd0")
					os.system("mkfs.vfat /dev/nbd0p1")
					os.system("mkfs.hfsplus -v OSX -J /dev/nbd0p2")
					os.system("qemu-nbd --disconnect /dev/nbd0")



def info(hostdata, tempdir):
	print(hostdata["hostname"])
	os.system("virsh dominfo " + hostdata["hostname"] + "")



def boot(hostdata, tempdir, force = False):
	print(" generate xml for libvirt")
	cwd = os.getcwd()
	diskimages = diskimages_get(hostdata, tempdir)
	## Build Host-XML ##
	lvxml = ""
	if hostdata["os"] == "osx":
		#osxversion = "Mojave"
		osxversion = "Catalina"
		lvxml += "<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>\n"
		lvxml += "  <name>" + hostdata["hostname"] + "</name>\n"
		## machine ##
		lvxml += "  <memory unit='KiB'>" + str(hostdata["memory"] * 1024) + "</memory>\n"
		lvxml += "  <currentMemory unit='KiB'>" + str(hostdata["memory"] * 1024) + "</currentMemory>\n"
		lvxml += "  <vcpu placement='static'>" + str(hostdata["vcpu"]) + "</vcpu>\n"
		lvxml += "  <os>\n"
		lvxml += "    <type arch='x86_64' machine='q35'>hvm</type>\n"
		lvxml += "    <loader readonly='yes' type='pflash'>" + cwd + "/files/osx/OVMF_CODE.fd</loader>\n"
		lvxml += "    <nvram>" + cwd + "/files/osx/OVMF_VARS-1024x768.fd</nvram>\n"
		lvxml += "  </os>\n"
		lvxml += "  <features>\n"
		lvxml += "    <acpi/>\n"
		lvxml += "    <kvm>\n"
		lvxml += "      <hidden state='on'/>\n"
		lvxml += "    </kvm>\n"
		lvxml += "  </features>\n"
		lvxml += "  <clock offset='utc'/>\n"
		lvxml += "  <on_poweroff>destroy</on_poweroff>\n"
		lvxml += "  <on_reboot>restart</on_reboot>\n"
		lvxml += "  <on_crash>restart</on_crash>\n"
		lvxml += "  <devices>\n"
		lvxml += "    <emulator>/usr/bin/qemu-system-x86_64</emulator>\n"
		lvxml += "    <disk type='file' device='disk'>\n"
		lvxml += "      <driver name='qemu' type='qcow2' cache='writeback'/>\n"
		lvxml += "      <source file='" + cwd + "/files/osx/" + osxversion + "/CloverNG.qcow2'/>\n"
		lvxml += "      <target dev='sda' bus='sata'/>\n"
		lvxml += "      <boot order='1'/>\n"
		lvxml += "      <address type='drive' controller='0' bus='0' target='0' unit='0'/>\n"
		lvxml += "    </disk>\n"
		for disk in hostdata["disks"]:
			lvxml += "    <disk type='file' device='disk'>\n"
			if diskimages[disk].endswith(".qcow2"):
				lvxml += "      <driver name='qemu' type='qcow2' cache='writeback'/>\n"
			else:
				lvxml += "      <driver name='qemu' />\n"
			lvxml += "      <source file='" + cwd + "/" + diskimages[disk] + "'/>\n"
			lvxml += "      <target dev='sdb' bus='sata'/>\n"
			lvxml += "      <boot order='2'/>\n"
			lvxml += "      <address type='drive' controller='0' bus='0' target='0' unit='1'/>\n"
			lvxml += "    </disk>\n"
			break
		lvxml += "    <disk type='file' device='disk'>\n"
		lvxml += "      <driver name='qemu' type='raw' cache='writeback'/>\n"
		lvxml += "      <source file='" + cwd + "/files/osx/" + osxversion + "/BaseSystem.img'/>\n"
		lvxml += "      <target dev='sdc' bus='sata'/>\n"
		lvxml += "      <boot order='3'/>\n"
		lvxml += "      <address type='drive' controller='0' bus='0' target='0' unit='2'/>\n"
		lvxml += "    </disk>\n"
		lvxml += "    <controller type='sata' index='0'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x1f' function='0x2'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='usb' index='0' model='ich9-ehci1'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x1d' function='0x7'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='usb' index='0' model='ich9-uhci1'>\n"
		lvxml += "      <master startport='0'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x1d' function='0x0' multifunction='on'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='usb' index='0' model='ich9-uhci2'>\n"
		lvxml += "      <master startport='2'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x1d' function='0x1'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='usb' index='0' model='ich9-uhci3'>\n"
		lvxml += "      <master startport='4'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x1d' function='0x2'/>\n"
		lvxml += "    </controller>\n"
		slotn = 2
		for interface in hostdata["network"]["interfaces"]:
			if "bridge" in hostdata["network"]["interfaces"][interface]:
				lvxml += "    <interface type='bridge'>\n"
				lvxml += "      <source bridge='" + hostdata["network"]["interfaces"][interface]["bridge"] + "'/>\n"
				lvxml += "      <virtualport type='openvswitch'/>\n"
			else:
				lvxml += "    <interface type='network'>\n"
				lvxml += "      <source network='default'/>\n"
			lvxml += "      <model type='e1000-82545em'/>\n"
			if "hwaddr" in hostdata["network"]["interfaces"][interface]:
				lvxml += "      <mac address='" + hostdata["network"]["interfaces"][interface]["hwaddr"] + "'/>\n"
			lvxml += "      <address type='pci' domain='0x0000' bus='0x02' slot='0x0" + str(slotn) + "' function='0x0'/>\n"
			lvxml += "    </interface>\n"
			slotn += 1
		lvxml += "    <input type='keyboard' bus='usb'>\n"
		lvxml += "      <address type='usb' bus='0' port='2'/>\n"
		lvxml += "    </input>\n"
		lvxml += "    <input type='mouse' bus='ps2'/>\n"
		lvxml += "    <input type='tablet' bus='usb'>\n"
		lvxml += "      <address type='usb' bus='0' port='3'/>\n"
		lvxml += "    </input>\n"
		lvxml += "    <input type='keyboard' bus='ps2'/>\n"
		lvxml += "    <graphics type='spice' autoport='yes'>\n"
		lvxml += "      <listen type='address'/>\n"
		lvxml += "    </graphics>\n"
		lvxml += "    <sound model='ich9'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x02' slot='0x01' function='0x0'/>\n"
		lvxml += "    </sound>\n"
		lvxml += "    <video>\n"
		lvxml += "      <model type='qxl' ram='65536' vram='65536' vgamem='16384' heads='1' primary='yes'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x0'/>\n"
		lvxml += "    </video>\n"
		lvxml += "    <redirdev bus='usb' type='spicevmc'>\n"
		lvxml += "      <address type='usb' bus='0' port='5'/>\n"
		lvxml += "    </redirdev>\n"
		lvxml += "    <hub type='usb'>\n"
		lvxml += "      <address type='usb' bus='0' port='1'/>\n"
		lvxml += "    </hub>\n"
		lvxml += "    <memballoon model='none'/>\n"
		lvxml += "  </devices>\n"
		lvxml += "  <!-- Note: Enable the next line when SELinux is enabled -->\n"
		lvxml += "  <!-- seclabel type='dynamic' model='selinux' relabel='yes'/> -->\n"
		lvxml += "  <qemu:commandline>\n"
		lvxml += "    <qemu:arg value='-device'/>\n"
		lvxml += "    <qemu:arg value='isa-applesmc,osk=ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc'/>\n"
		lvxml += "    <qemu:arg value='-smbios'/>\n"
		lvxml += "    <qemu:arg value='type=2'/>\n"
		lvxml += "    <qemu:arg value='-cpu'/>\n"
		lvxml += "    <qemu:arg value='Penryn,kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on,+pcid,+ssse3,+sse4.2,+popcnt,+avx,+aes,+xsave,+xsaveopt,check'/>\n"
		lvxml += "  </qemu:commandline>\n"
		lvxml += "</domain>\n"
	else:
		lvxml += "<domain type='kvm'>\n"
		## general ##
		lvxml += "  <name>" + hostdata["hostname"] + "</name>\n"
		## machine ##
		lvxml += "  <memory unit='KiB'>" + str(hostdata["memory"] * 1024) + "</memory>\n"
		lvxml += "  <currentMemory unit='KiB'>" + str(hostdata["memory"] * 1024) + "</currentMemory>\n"
		lvxml += "  <vcpu placement='static'>" + str(hostdata["vcpu"]) + "</vcpu>\n"
		## os ##
		lvxml += "  <os>\n"
		lvxml += "    <type arch='x86_64' machine='pc-i440fx-cosmic'>hvm</type>\n"
		#lvxml += "    <boot dev='hd'/>\n"
		#lvxml += "    <boot dev='cdrom'/>\n"
		lvxml += "  </os>\n"
		## features ##
		lvxml += "  <features>\n"
		lvxml += "    <acpi/>\n"
		lvxml += "    <apic/>\n"
		lvxml += "    <vmport state='off'/>\n"
		lvxml += "  </features>\n"
		## cpu mode ##
		lvxml += "  <cpu mode='custom' match='exact' check='partial'>\n"
		lvxml += "    <model fallback='allow'>SandyBridge-IBRS</model>\n"
		lvxml += "  </cpu>\n"
		lvxml += "  <clock offset='utc'>\n"
		lvxml += "    <timer name='rtc' tickpolicy='catchup'/>\n"
		lvxml += "    <timer name='pit' tickpolicy='delay'/>\n"
		lvxml += "    <timer name='hpet' present='no'/>\n"
		lvxml += "  </clock>\n"
		lvxml += "  <on_poweroff>destroy</on_poweroff>\n"
		lvxml += "  <on_reboot>restart</on_reboot>\n"
		lvxml += "  <on_crash>destroy</on_crash>\n"
		lvxml += "  <pm>\n"
		lvxml += "    <suspend-to-mem enabled='no'/>\n"
		lvxml += "    <suspend-to-disk enabled='no'/>\n"
		lvxml += "  </pm>\n"
		## devices ##
		lvxml += "  <devices>\n"
		lvxml += "    <emulator>/usr/bin/kvm-spice</emulator>\n"
		lvxml += "    <redirdev bus='usb' type='spicevmc'>\n"
		lvxml += "      <address type='usb' bus='0' port='2'/>\n"
		lvxml += "    </redirdev>\n"
		lvxml += "    <redirdev bus='usb' type='spicevmc'>\n"
		lvxml += "      <address type='usb' bus='0' port='3'/>\n"
		lvxml += "    </redirdev>\n"
		## memory ##
		lvxml += "    <memballoon model='virtio'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>\n"
		lvxml += "    </memballoon>\n"
		## disks ##
		for disk in hostdata["disks"]:
			lvxml += "    <disk type='file' device='disk'>\n"
			if diskimages[disk].endswith(".qcow2"):
				lvxml += "      <driver name='qemu' type='qcow2'/>\n"
			else:
				lvxml += "      <driver name='qemu' />\n"
			lvxml += "      <source file='" + cwd + "/" + diskimages[disk] + "'/>\n"
			if hostdata["os"] == "freebsd":
				lvxml += "      <target dev='hda' bus='sata'/>\n"
				lvxml += "      <address type='drive' controller='1' bus='0' target='0' unit='0'/>\n"
			elif hostdata["os"] == "windows":
				lvxml += "      <target dev='sda' bus='sata'/>\n"
				lvxml += "      <address type='drive' controller='1' bus='0' target='0' unit='0'/>\n"
			else:
				lvxml += "      <target dev='vda' bus='virtio'/>\n"
				lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>\n"
			lvxml += "      <boot order='1'/>\n"
			lvxml += "    </disk>\n"
			break
		if "iso" in hostdata:
			lvxml += "    <disk type='file' device='cdrom'>\n"
			lvxml += "      <driver name='qemu' type='raw'/>\n"
			lvxml += "      <source file='" + cwd + "/" + tempdir + "/auto.iso'/>\n"
			if hostdata["os"] == "freebsd":
				lvxml += "      <target dev='hdb' bus='ide'/>\n"
			else:
				lvxml += "      <target dev='hda' bus='ide'/>\n"
			lvxml += "      <readonly/>\n"
			lvxml += "      <address type='drive' controller='0' bus='0' target='0' unit='0'/>\n"
			lvxml += "      <boot order='2'/>\n"
			lvxml += "    </disk>\n"
		## controller ##
		lvxml += "    <controller type='usb' index='0' model='ich9-ehci1'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x7'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='usb' index='0' model='ich9-uhci1'>\n"
		lvxml += "      <master startport='0'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0' multifunction='on'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='usb' index='0' model='ich9-uhci2'>\n"
		lvxml += "      <master startport='2'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x1'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='usb' index='0' model='ich9-uhci3'>\n"
		lvxml += "      <master startport='4'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x2'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='pci' index='0' model='pci-root'/>\n"
		lvxml += "    <controller type='ide' index='0'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>\n"
		lvxml += "    </controller>\n"
		lvxml += "    <controller type='virtio-serial' index='0'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>\n"
		lvxml += "    </controller>\n"
		## network ##
		slotn = 1
		for interface in hostdata["network"]["interfaces"]:
			if "bridge" in hostdata["network"]["interfaces"][interface]:
				lvxml += "    <interface type='bridge'>\n"
				lvxml += "      <source bridge='" + hostdata["network"]["interfaces"][interface]["bridge"] + "'/>\n"
				lvxml += "      <virtualport type='openvswitch'/>\n"
			else:
				lvxml += "    <interface type='network'>\n"
				lvxml += "      <source network='default'/>\n"
			if hostdata["os"] == "windows":
				lvxml += "      <model type='rtl8139'/>\n"
			else:
				lvxml += "      <model type='virtio'/>\n"
			if "hwaddr" in hostdata["network"]["interfaces"][interface]:
				lvxml += "      <mac address='" + hostdata["network"]["interfaces"][interface]["hwaddr"] + "'/>\n"
			lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x1" + str(slotn) + "' function='0x0'/>\n"
			lvxml += "      <boot order='3'/>\n"
			lvxml += "    </interface>\n"
			slotn += 1
		## console ##
		lvxml += "    <serial type='pty'>\n"
		lvxml += "      <target type='isa-serial' port='0'>\n"
		lvxml += "        <model name='isa-serial'/>\n"
		lvxml += "      </target>\n"
		lvxml += "    </serial>\n"
		lvxml += "    <console type='pty'>\n"
		lvxml += "      <target type='serial' port='0'/>\n"
		lvxml += "    </console>\n"
		lvxml += "    <channel type='spicevmc'>\n"
		lvxml += "      <target type='virtio' name='com.redhat.spice.0'/>\n"
		lvxml += "      <address type='virtio-serial' controller='0' bus='0' port='1'/>\n"
		lvxml += "    </channel>\n"
		## inputs ##
		lvxml += "    <input type='tablet' bus='usb'>\n"
		lvxml += "      <address type='usb' bus='0' port='1'/>\n"
		lvxml += "    </input>\n"
		lvxml += "    <input type='mouse' bus='ps2'/>\n"
		lvxml += "    <input type='keyboard' bus='ps2'/>\n"
		## video ##
		lvxml += "    <graphics type='spice' autoport='yes'>\n"
		lvxml += "      <listen type='address'/>\n"
		lvxml += "      <image compression='off'/>\n"
		lvxml += "    </graphics>\n"
		lvxml += "    <video>\n"
		lvxml += "      <model type='qxl' ram='65536' vram='65536' vgamem='16384' heads='1' primary='yes'/>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>\n"
		lvxml += "    </video>\n"
		## sound ##
		lvxml += "    <sound model='ich6'>\n"
		lvxml += "      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>\n"
		lvxml += "    </sound>\n"
		lvxml += "  </devices>\n"
		lvxml += "</domain>\n"

	with open(tempdir + "/lvxml", "w") as ofile:
		ofile.write(lvxml)

	if force == True:
		print(" stop and remove old vguest if running")
		if hostdata["os"] == "osx":
			os.system("virsh undefine --nvram " + hostdata["hostname"] + " 2>/dev/null >/dev/null")
		os.system("virsh destroy " + hostdata["hostname"] + " 2>/dev/null >/dev/null")
		os.system("virsh undefine " + hostdata["hostname"] + " 2>/dev/null >/dev/null")

	print(" boot vguest")
	if hostdata["os"] == "osx":
		os.system("cp files/osx/OVMF_VARS-1024x768.fd.bak files/osx/OVMF_VARS-1024x768.fd")
	os.system("virsh define " + tempdir + "/lvxml >/dev/null")
	os.system("virsh start " + hostdata["hostname"] + " >/dev/null")



