#!/usr/bin/python3
#
#

import os
import sys
import json


def diskimages_get(hostdata, tempdir):
	diskimages = {}
	if "iso" in hostdata:
		for disk in hostdata["disks"]:
			diskimages[disk] = "libvirt/images/" + hostdata["hostname"] + "_" + disk + ".qcow2"
	elif "image" in hostdata:
		dn = 0
		for disk in hostdata["disks"]:
			if dn == 0:
				imgname = hostdata["image"].split("/")[-1]
				diskimages[disk] = "libvirt/images/" + hostdata["hostname"] + "_" + disk + "_" + imgname
			else:
				diskimages[disk] = "libvirt/images/" + hostdata["hostname"] + "_" + disk + ".qcow2"
			dn += 1
	return diskimages


def diskimages_create(hostdata, tempdir):
	print(" generate diskimages")
	diskimages = diskimages_get(hostdata, tempdir)
	if "iso" in hostdata:
		for disk in diskimages:
			if not os.path.exists(diskimages[disk]):
				print("  " + diskimages[disk] + " (" + hostdata["disks"][disk]["size"] + ")")
				os.system("qemu-img create -f qcow2 '" + diskimages[disk] + "' " + hostdata["disks"][disk]["size"] + " >/dev/null")
	elif "image" in hostdata:
		dn = 0
		for disk in diskimages:
			if not os.path.exists(diskimages[disk]):
				if dn == 0:
					print("  " + diskimages[disk])
					os.system("cp '" + hostdata["image"] + "' '" + diskimages[disk] + "'")
				else:
					print("  " + diskimages[disk] + " (" + hostdata["disks"][disk]["size"] + ")")
					os.system("qemu-img create -f qcow2 '" + diskimages[disk] + "' " + hostdata["disks"][disk]["size"] + " >/dev/null")
			dn += 1


def boot(hostdata, tempdir, force = False):
	print(" generate cmd for qemu")
	diskimages = diskimages_get(hostdata, tempdir)
	for disk in hostdata["disks"]:
		if not os.path.exists("libvirt/images/" + hostdata["hostname"] + "_" + disk + ".qcow2"):
			os.system("qemu-img create -f qcow2 libvirt/images/" + hostdata["hostname"] + "_" + disk + ".qcow2 " + hostdata["disks"][disk]["size"])
	qemu = "  qemu-system-x86_64 -enable-kvm -boot d"
	qemu += " -m 512"
	qemu += " -smp 2"
	qemu += "  -name \"" + hostdata["hostname"] + "\""
	for disk in hostdata["disks"]:
		qemu += " -hda /usr/src/testnetz/libvirt/images/" + hostdata["hostname"] + "_" + disk + ".qcow2"
		break
	qemu += " -cdrom /usr/src/testnetz/" + tempdir + "/auto.iso"
	for interface in hostdata["network"]["interfaces"]:
		if "hwaddr" in hostdata["network"]["interfaces"][interface]:
			qemu += " -net nic,vlan=1,macaddr=" + hostdata["network"]["interfaces"][interface]["hwaddr"] + " -net tap,vlan=1,script=\"/etc/qemu-ifup\""
		else:
			qemu += " -net nic,vlan=1 -net tap,vlan=1,script=\"/etc/qemu-ifup\""
		break
	print("")
	print(" boot vguest")
	print("")
	print("  " + qemu)
	print("")
