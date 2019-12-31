#!/usr/bin/python3
#
#

import os
import json
import mkisofs

def get_files():
	files = {}
	return files

def pxe(bootserver):
	isolinuxtxtnet = ""
	return isolinuxtxtnet

def autoseed(hostdata, tempdir, services):
	## generate configfiles ##
	os.system("mkdir -p " + tempdir + "/files/etc/sysconfig/network-scripts/")
	dns = ""
	resolv = "search " + hostdata["domainname"] + "\n"
	for nameserver in hostdata["network"]["nameservers"]:
		resolv += "nameserver " + nameserver + "\n"
		if dns == "":
			dns = nameserver
	with open(tempdir + "/files/etc/resolv.conf", "w") as ofile:
		ofile.write(resolv)
	hostname = hostdata["hostname"] + "." + hostdata["domainname"] + "\n"
	with open(tempdir + "/files/etc/hostname", "w") as ofile:
		ofile.write(hostname)
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				ifcfg = "#UUID=\"\"\n"
				ifcfg += "DNS1=\"" + dns + "\"\n"
				ifcfg += "IPADDR=\"" + ipv4["address"] + "\"\n"
				ifcfg += "GATEWAY=\"" + hostdata["network"]["gateway"] + "\"\n"
				ifcfg += "NETMASK=\"" + ipv4["netmask"] + "\"\n"
				ifcfg += "BOOTPROTO=\"static\"\n"
				ifcfg += "DEVICE=\"" + interface + "\"\n"
				ifcfg += "ONBOOT=\"yes\"\n"
				ifcfg += "IPV6INIT=\"yes\"\n"
				with open(tempdir + "/files/etc/sysconfig/network-scripts/ifcfg-" + interface + "", "w") as ofile:
					ofile.write(ifcfg)


	## generate setup script ##
	setup = "#!/bin/sh\n"
	setup += "\n"
	setup += "\n"
	setup += "\n"
	with open(tempdir + "/setup.sh", "w") as ofile:
		ofile.write(setup)

	postsh = ""
	postsh += "#!/bin/sh\n"
	postsh += "\n"
	postsh += "sed -i \"s|^#PermitRootLogin .*|PermitRootLogin yes|g\" /etc/ssh/sshd_config\n"
	postsh += "\n"
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			if "sshpubkey" in hostdata["users"][user]:
				postsh += "mkdir -p /root/.ssh\n"
				postsh += "chown root:root /root/.ssh\n"
				postsh += "chmod 700 /root/.ssh\n"
				postsh += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /root/.ssh/authorized_keys\n"
				postsh += "chown root:root /root/.ssh/authorized_keys\n"
				postsh += "chmod 600 /root/.ssh/authorized_keys\n"
				postsh += "\n"
		elif userflag == False:
			if "sshpubkey" in hostdata["users"][user]:
				postsh += "mkdir -p /home/" + user + "/.ssh\n"
				postsh += "chown " + user + ":" + user + " /home/" + user + "/.ssh\n"
				postsh += "chmod 700 /home/" + user + "/.ssh\n"
				postsh += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /home/" + user + "/.ssh/authorized_keys\n"
				postsh += "chown " + user + ":" + user + " /home/" + user + "/.ssh/authorized_keys\n"
				postsh += "chmod 600 /home/" + user + "/.ssh/authorized_keys\n"
				postsh += "\n"
	postsh += "\n"
	with open(tempdir + "/post.sh", "w") as ofile:
		ofile.write(postsh)

	if "iso" in hostdata:
		if not os.path.exists(tempdir + "/auto.iso"):
			# mod fetch-macOS.py to get the right image without manuel selction
			# ./fetch-macOS.py -h -> isoimages/OSX-BaseSystem.img
			# copy isoimages/OSX-BaseSystem.img tempdir + "/auto.iso"
			print("")




