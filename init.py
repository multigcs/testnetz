#!/usr/bin/python3
#
#

import os
import sys
import glob
import json
import copy
import importlib

from systems import ubuntu
from systems import centos
from systems import opensuse
from systems import freebsd
from systems import openbsd
from systems import openwrt
from systems import windows
from systems import osx

from targets import libvirt
from targets import docker
from targets import qemu

servicenames = []
for servicefile in glob.glob("services/*.py"):
    servicename = servicefile.split("/")[1].split(".")[0]
    print(f"importing: {servicename}")
    exec(f"from services import {servicename}")
    servicenames.append(servicename)

bootserver = "192.168.122.1"


def deepupdate(target, src):
	for k, v in src.items():
		if k in target:
			for k2, v2 in src[k].items():
				if k2 in target[k]:
					target[k][k2]+=v2
				else:
					target[k][k2] = v2
		else:
			target[k] = copy.deepcopy(v)

def load_hostfile(hostfile):
	hostdata = {}
	with open(hostfile) as json_file:
		hostdata_tmp = json.load(json_file)
		hostdata_tmp["hostid"] = hostfile.split("/")[-1].split(".")[0]
		if "includes" in hostdata_tmp:
			for include in hostdata_tmp["includes"]:
				with open(include) as json_inc:
					hostdata_inc = json.load(json_inc)
					deepupdate(hostdata, hostdata_inc)
		deepupdate(hostdata, hostdata_tmp)
	print (hostdata)
	return hostdata


force = False
test = False
csv = False
cmkbulk = False
inventory = False
info = False
menu = False
hostfiles = []
if len(sys.argv) == 1:
	print("USAGE: init.py [-f|-i|-t|-c|-m] JSONFILE [JSONFILE ...]")
	exit(1)
else:
	for argv in sys.argv[1:]:
		if argv == "-t":
			test = True
		elif argv == "-f":
			force = True
		elif argv == "-c":
			csv = True
		elif argv == "-m":
			menu = True
		elif argv == "--cmkbulk":
			cmkbulk = True
		elif argv == "--inventory":
			inventory = True
		elif argv == "-i":
			info = True
		elif argv == "-p":

			## copy tftp-files ##
			os.system("mkdir -p /var/lib/tftpboot/")
			os.system("cp -a files/pxe/* /var/lib/tftpboot/")

			isolinuxtxtnet = ""
			isolinuxtxtnet += "UI vesamenu.c32\n"
			isolinuxtxtnet += "MENU INCLUDE graphics.conf\n"
			isolinuxtxtnet += "MENU TITLE Installer\n"
			isolinuxtxtnet += "PROMPT 0\n"
			isolinuxtxtnet += "TIMEOUT 0\n"
			isolinuxtxtnet += "\n"
			isolinuxtxtnet += "DEFAULT main\n"
			isolinuxtxtnet += "\n"
			isolinuxtxtnet += "LABEL main\n"
			isolinuxtxtnet += "  MENU LABEL Return to Main Menu...\n"
			isolinuxtxtnet += "  KERNEL vesamenu.c32\n"
			isolinuxtxtnet += "  APPEND pxelinux.cfg/default\n"
			isolinuxtxtnet += "\n"
			isolinuxtxtnet += "MENU SEPARATOR\n"
			isolinuxtxtnet += "\n"
			isolinuxtxtnet += ubuntu.pxe(bootserver)
			isolinuxtxtnet += centos.pxe(bootserver)
			isolinuxtxtnet += opensuse.pxe(bootserver)
			isolinuxtxtnet += windows.pxe(bootserver)
			isolinuxtxtnet += freebsd.pxe(bootserver)
			isolinuxtxtnet += openbsd.pxe(bootserver)
			isolinuxtxtnet += openwrt.pxe(bootserver)
			print(isolinuxtxtnet)
			with open("/var/lib/tftpboot/install.conf", "w") as ofile:
				ofile.write(isolinuxtxtnet)

			exit(0)
		else:
			hostfiles.append(argv)

if not os.path.exists("temp"):
	os.mkdir("temp")


if menu == True:
	import whiptail
	whip = whiptail.Whiptail("Testnetz", "Host-Select", 20, 80)
	menu = []
	mn = 1
	for hostfile in glob.glob("hosts/*.json"):
		hostdata = load_hostfile(hostfile)
		menu.append([str(mn), hostdata["hostname"]])
		mn = mn + 1
	ret = whip.menu("Init Host", menu)
	mn = 1
	for hostfile in glob.glob("hosts/*.json"):
		if int(ret) == int(mn):
			print (hostfile)
			force = True
			hostfiles.append(hostfile)
		mn = mn + 1



if csv == True:
	for hostfile in hostfiles:
		hostdata = load_hostfile(hostfile)
		for dev in hostdata["network"]["interfaces"]:
			for ipv4 in hostdata["network"]["interfaces"][dev]["ipv4"]:
				print(hostfile + ";" + hostdata["hostname"] + ";" + hostdata["os"] + ";" + dev + ";" + ipv4["address"] + ";" + ipv4["netmask"])

elif cmkbulk == True:
	print("hostname;ip address;agent")
	for hostfile in hostfiles:
		hostdata = load_hostfile(hostfile)
		exist = False
		for dev in hostdata["network"]["interfaces"]:
			for ipv4 in hostdata["network"]["interfaces"][dev]["ipv4"]:
				if exist == False:
					print(hostdata["hostname"] + ";" + ipv4["address"] + ";cmk-agent")
					exist = True


elif inventory == True:
	oss = {}
	for hostfile in hostfiles:
		hostdata = load_hostfile(hostfile)
		oss[hostdata["os"]] = hostdata["os"]
	for os in oss:
		print("[" + os + "]")
		for hostfile in hostfiles:
			hostdata = load_hostfile(hostfile)
			exist = False
			if hostdata["os"] == os:
				for dev in hostdata["network"]["interfaces"]:
					for ipv4 in hostdata["network"]["interfaces"][dev]["ipv4"]:
						if exist == False:
							if hostdata["os"] == "centos" or hostdata["os"] == "ubuntu" or hostdata["os"] == "debian" or hostdata["os"] == "opensuse":
								print(hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_python_interpreter=/usr/bin/python3")
							elif hostdata["os"] == "windows":
								print(hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_user=administrator ansible_password=admin ansible_port=5986 ansible_connection=winrm ansible_winrm_server_cert_validation=ignore")
							elif hostdata["os"] == "osx":
								print(hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_python_interpreter=/usr/bin/python ansible_user=oliver")
							elif hostdata["os"] == "openbsd" or hostdata["os"] == "freebsd":
								print(hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_python_interpreter=/usr/local/bin/python3")
							else:
								print(hostdata["hostname"] + " ansible_host=" + ipv4["address"] + "")
							exist = True
		print("")




elif test == True:
	ips = {}
	macs = {}
	names = {}
	test = True
	for hostfile in hostfiles:
		print(hostfile)
		hostdata = load_hostfile(hostfile)
		if "hostname" not in hostdata:
			print("Hostname not found")
			test = False
		else:
			print(" Hostname: " + hostdata["hostname"])
			if hostdata["hostname"] in names:
				print(" # Hostname allready exist: " + names[hostdata["hostname"]])
				test = False
			else:
				names[hostdata["hostname"]] = hostfile
		if "network" not in hostdata:
			print(" # Network section not found")
			test = False
		else:
			if "interfaces" not in hostdata["network"]:
				print(" # Interfaces section not found")
				test = False
			else:
				for dev in hostdata["network"]["interfaces"]:
					print(" network-interface: " + dev)
					if "hwaddr" not in hostdata["network"]["interfaces"][dev]:
						print("  # hwaddr not found in interface " + dev)
						#test = False
					else:
						print("  hwaddr: " + hostdata["network"]["interfaces"][dev]["hwaddr"])
						if hostdata["network"]["interfaces"][dev]["hwaddr"] in macs:
							print("  # hwaddr allready exist: " + macs[hostdata["network"]["interfaces"][dev]["hwaddr"]])
							test = False
						else:
							macs[hostdata["network"]["interfaces"][dev]["hwaddr"]] = hostfile
					if "ipv4" not in hostdata["network"]["interfaces"][dev]:
						print(" # ipv4 section not found")
						test = False
					else:
						for ipv4 in hostdata["network"]["interfaces"][dev]["ipv4"]:
							if "address" not in ipv4:
								print("   # no address in ipv4")
								test = False
							else:
								print("  ipv4: " + ipv4["address"])
								if ipv4["address"] in ips:
									print("  # ip allready exist: " + ips[ipv4["address"]])
									test = False
								else:
									ips[ipv4["address"]] = hostfile
	print("")
	if test == True:
		print("All Right")
	else:
		print("Found errors")
	print("")


else:
	for hostfile in hostfiles:
		hostdata = load_hostfile(hostfile)
		tempdir = "temp/" + hostdata["hostname"]
		if "bootserver" not in hostdata:
			hostdata["bootserver"] = bootserver

		## set diskimage names ##
		if hostdata["target"] == "libvirt" or hostdata["target"] == "pxe":
			diskimages = libvirt.diskimages_get(hostdata, tempdir)
		elif hostdata["target"] == "qemu":
			diskimages = qemu.diskimages_get(hostdata, tempdir)
		elif hostdata["target"] == "docker":
			diskimages = docker.diskimages_get(hostdata, tempdir)

		## show info ##
		if info == True:
			if hostdata["target"] == "libvirt" or hostdata["target"] == "pxe":
				libvirt.info(hostdata, tempdir)
			elif hostdata["target"] == "docker":
				docker.info(hostdata, tempdir)
			continue

		print("hostfile: " + hostfile)
		print(" hostname: " + hostdata["hostname"])

		## remove old temp files and images ##
		if force == True:
			print(" remove old temp files and images")
			if os.path.exists(tempdir):
				print("  rm -rf 'temp/" + hostdata["hostname"] + "'")
				os.system("rm -rf 'temp/" + hostdata["hostname"] + "'")
			for disk in diskimages:
				if os.path.exists(diskimages[disk]):
					print("  rm -rf '" + diskimages[disk] + "'")
					os.system("rm -rf '" + diskimages[disk] + "'")

		## create temp dir ##
		if not os.path.exists("isoimages"):
			os.mkdir("isoimages")
		if not os.path.exists("libvirt"):
			os.mkdir("libvirt")
		if not os.path.exists("libvirt/images"):
			os.mkdir("libvirt/images")
		if not os.path.exists(tempdir):
			os.mkdir(tempdir)

		## create diskimages ##
		if hostdata["target"] == "libvirt" or hostdata["target"] == "pxe":
			diskimages = libvirt.diskimages_create(hostdata, tempdir)
		elif hostdata["target"] == "qemu":
			diskimages = qemu.diskimages_create(hostdata, tempdir)

		## create service installer scripts ##
		services = []
		if "services" in hostdata:
			if not os.path.exists(tempdir + "/services"):
				os.mkdir(tempdir + "/services")
			for servicename in servicenames:
				exec(f"services.append({servicename}.setup(hostdata, '{tempdir}/services'))")

		## create autoinstaller ##
		print(" create autoinstaller for " + hostdata["os"] + "")
		if hostdata["os"] == "ubuntu" or hostdata["os"] == "debian":
			ubuntu.autoseed(hostdata, tempdir, services)
		elif hostdata["os"] == "centos" or hostdata["os"] == "fedora":
			centos.autoseed(hostdata, tempdir, services)
		elif hostdata["os"] == "opensuse":
			opensuse.autoseed(hostdata, tempdir, services)
		elif hostdata["os"] == "windows":
			windows.autoseed(hostdata, tempdir, services)
		elif hostdata["os"] == "freebsd":
			freebsd.autoseed(hostdata, tempdir, services)
		elif hostdata["os"] == "openbsd":
			openbsd.autoseed(hostdata, tempdir, services)
		elif hostdata["os"] == "openwrt":
			openwrt.autoseed(hostdata, tempdir, services)


		## boot guest system ##
		if hostdata["target"] == "libvirt" or hostdata["target"] == "pxe":
			libvirt.boot(hostdata, tempdir, force)
		elif hostdata["target"] == "docker":
			docker.boot(hostdata, tempdir, force)
		elif hostdata["target"] == "qemu":
			qemu.boot(hostdata, tempdir, force)





