#!/usr/bin/python3
#
#

import os
import json
import mkisofs
import blowfish
import bcrypt
import isoparser

# pkg_add python-3.6.8p0

def get_files():
	files = {}
	files["isoimages/OpenBSD-cd66.iso"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/cd66.iso"
	files["files/openbsd/tftp/openbsd6.6/auto_install"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/pxeboot"
	files["files/openbsd/tftp/openbsd6.6/bsd.rd"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/bsd.rd"
	files["files/openbsd/tftp/bsd"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/bsd.rd"
	files["files/openbsd/http/openbsd-6.6/amd64/index.txt"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/index.txt"
	files["files/openbsd/http/openbsd-6.6/amd64/SHA256.sig"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/SHA256.sig"
	files["files/openbsd/http/openbsd-6.6/amd64/man66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/man66.tgz"
	files["files/openbsd/http/openbsd-6.6/amd64/xshare66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/xshare66.tgz"
	files["files/openbsd/http/openbsd-6.6/amd64/base66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/base66.tgz"
	files["files/openbsd/http/openbsd-6.6/amd64/game66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/game66.tgz"
	files["files/openbsd/http/openbsd-6.6/amd64/xserv66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/xserv66.tgz"
	files["files/openbsd/http/openbsd-6.6/amd64/comp66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/comp66.tgz"
	files["files/openbsd/http/openbsd-6.6/amd64/xbase66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/xbase66.tgz"
	files["files/openbsd/http/openbsd-6.6/amd64/xfont66.tgz"] = "https://cdn.openbsd.org/pub/OpenBSD/6.6/amd64/xfont66.tgz"
	return files


def pxe(bootserver):
	for rfile in get_files():
		if rfile.startswith("files/"):
			if not os.path.exists(rfile):
				print("  Get missing file: " + rfile + " ...")
				os.system("mkdir -p " + os.path.dirname(rfile))
				os.system("wget -O " + rfile + " " + get_files()[rfile])
	os.system("cp -auv files/openbsd/tftp/* /var/lib/tftpboot/")
	os.system("cp -auv files/openbsd/http/* /var/www/html/")
	isolinuxtxtnet = ""
	for version in ["6.6"]:
		isolinuxtxtnet += "LABEL openbsd" + version.replace(".", "") + "\n"
		isolinuxtxtnet += "  MENU LABEL OpenBSD: " + version + "\n"
		isolinuxtxtnet += "  KERNEL pxechn.c32\n"
		isolinuxtxtnet += "  APPEND openbsd" + version + "/auto_install\n"
		isolinuxtxtnet += "\n"
	return isolinuxtxtnet

def autoseed(hostdata, tempdir, services):
	isocheck = False
	if "iso" in hostdata:
		if not os.path.exists(hostdata["iso"]):
			print("  ISO not found on local filesystem (" + hostdata["iso"] + ")...")
			rfiles = get_files()
			if hostdata["iso"] in rfiles:
				print("   Get ISO from " + rfiles[hostdata["iso"]] + "...")
				os.system("wget -O " + hostdata["iso"] + " " + rfiles[hostdata["iso"]])
			else:
				return
		isoinfo = os.popen("isoinfo -d -i " + hostdata["iso"]).read()
		for line in isoinfo.split("\n"):
			if line.startswith("Volume id: "):
				isoname = line.split(":", 1)[1].strip()
				isoversion = isoname.split()[1]
				isoarch = isoname.split()[0].split("/")[1]
				print(isoname, isoarch, isoversion)
				if isoname.startswith("OpenBSD/"):
					isocheck = True
	if isocheck == True:
		print("  ISO-Name:    " + isoname)
		print("  ISO-Version: " + isoversion)
		print("  ISO-Arch:    " + isoarch)
	## generate setup script ##
	setup = "#!/bin/sh\n"
	setup += "\n"
	setup += "## hostname ##\n"
	setup += "echo \"" + hostdata["hostname"] + "." + hostdata["domainname"] + "\" > /etc/myname\n"
	setup += "hostname '" + hostdata["hostname"] + "." + hostdata["domainname"] + "'\n"
	setup += "domainname '" + hostdata["domainname"] + "'\n"
	setup += "\n"
	setup += "## resolv.conf ##\n"
	setup += "cat <<EOF > /etc/resolv.conf\n"
	setup += "search " + hostdata["domainname"] + "\n"
	dns = ""
	for nameserver in hostdata["network"]["nameservers"]:
		setup += "nameserver " + nameserver + "\n"
		if dns == "":
			dns = nameserver
	setup += "EOF\n"
	setup += "\n"
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				setup += "## interface: " + interface + " ##\n"
				setup += "ifconfig " + interface + " " + ipv4["address"] + " netmask " + ipv4["netmask"] + "\n"
				setup += "route add default " + hostdata["network"]["gateway"] + "\n"
				setup += "echo \"inet " + ipv4["address"] + " " + ipv4["netmask"] + " NONE\" > /etc/hostname." + interface + "\n"
				setup += "\n"
	setup += "## sshd_config ##\n"
	setup += "sed -i \"s|^#PermitRootLogin .*|PermitRootLogin yes|g\" /etc/ssh/sshd_config\n"
	setup += "\n"
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			if "sshpubkey" in hostdata["users"][user]:
				setup += "## authorized_keys (" + user + ") ##\n"
				setup += "mkdir -p /root/.ssh\n"
				setup += "chown root:root /root/.ssh\n"
				setup += "chmod 700 /root/.ssh\n"
				setup += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /root/.ssh/authorized_keys\n"
				setup += "chown root:root /root/.ssh/authorized_keys\n"
				setup += "chmod 600 /root/.ssh/authorized_keys\n"
				setup += "\n"
		else:
			setup += "## add user (" + user + ") ##\n"
			setup += "useradd " + user + "\n"
			setup += "echo -e \"" + hostdata["users"][user]["password"] + "\\n" + hostdata["users"][user]["password"] + "\\n\" | passwd " + user + "\n"
			setup += "\n"
			if "sshpubkey" in hostdata["users"][user]:
				setup += "## authorized_keys (" + user + ") ##\n"
				setup += "mkdir -p /home/" + user + "/.ssh\n"
				setup += "chown " + user + ":" + user + " /home/" + user + "/.ssh\n"
				setup += "chmod 700 /home/" + user + "/.ssh\n"
				setup += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /home/" + user + "/.ssh/authorized_keys\n"
				setup += "chown " + user + ":" + user + " /home/" + user + "/.ssh/authorized_keys\n"
				setup += "chmod 600 /home/" + user + "/.ssh/authorized_keys\n"
				setup += "\n"
	setup += "\n"
	with open(tempdir + "/setup.sh", "w") as ofile:
		ofile.write(setup)
	autoseed = ""
	autoseed += "System hostname = " + hostdata["hostname"] + "\n"
	for interface in hostdata["network"]["interfaces"]:
		autoseed += "Which network interface do you wish to configure = " + interface + "\n"
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				autoseed += "IPv4 address for " + interface + " = " + ipv4["address"] + "\n"
				autoseed += "Netmask for " + interface + " = " + ipv4["netmask"] + "\n"
				autoseed += "IPv6 address for " + interface + " = none\n"
		else:
			autoseed += "IPv4 address for " + interface + " = dhcp\n"
	autoseed += "Which network interface do you wish to configure = done\n"
	autoseed += "Default IPv4 route = " + hostdata["network"]["gateway"] + "\n"
	autoseed += "DNS domain name = " + hostdata["domainname"] + "\n"
	for nameserver in hostdata["network"]["nameservers"]:
		autoseed += "DNS nameserver = " + nameserver + "\n"
		break
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			pwhash = os.popen("htpasswd -bnBC 10 '' " + hostdata["users"][user]["password"] + " | tr -d ':\n' | sed 's/$2y/$2a/'").read()
			autoseed += "Password for " + user + " account = " + pwhash + "\n"
			autoseed += "Password for " + user + " account = $2a$10$WPcwSykNvzgwqq16mn.I2Ofloy8OoMKORhJgVd.hLPIycEgpKjr2m\n"
			if "sshpubkey" in hostdata["users"][user]:
				autoseed += "Public ssh key for " + user + " account = " + hostdata["users"][user]["sshpubkey"] + "\n"
		else:
			userflag = True
			pwhash = os.popen("htpasswd -bnBC 10 '' " + hostdata["users"][user]["password"] + " | tr -d ':\n' | sed 's/$2y/$2a/'").read()
			autoseed += "Setup a user = " + user + "\n"
			autoseed += "Password for user " + user + " = " + pwhash + "\n"
			autoseed += "Password for user " + user + " = $2a$10$WPcwSykNvzgwqq16mn.I2Ofloy8OoMKORhJgVd.hLPIycEgpKjr2m\n"
			autoseed += "Full name for user " + user + " = " + user + "\n"
			if "sshpubkey" in hostdata["users"][user]:
				autoseed += "Public ssh key for user " + user + " = " + hostdata["users"][user]["sshpubkey"] + "\n"
	autoseed += "Start sshd(8) by default = yes\n"
	autoseed += "Allow root ssh login = yes\n"
	autoseed += "Do you expect to run the X Window System = no\n"
	autoseed += "What timezone are you in = Europe/Berlin\n"
	autoseed += "Which disk is the root disk = sd0\n"
	autoseed += "Use (W)hole disk MBR, whole disk (G)PT, (O)penBSD area or (E)dit = OpenBSD\n"
	autoseed += "Use (A)uto layout, (E)dit auto layout, or create (C)ustom layout = a\n"
	if hostdata["target"] == "pxe" and "version" in hostdata:
		autoseed += "Location of sets = http\n"
		autoseed += "HTTP Server = " + hostdata["bootserver"] + "\n"
		autoseed += "Server directory = openbsd-" + hostdata["version"] + "/amd64\n"
		autoseed += "Use http instead = yes\n"
	elif "iso" in hostdata:
		autoseed += "Location of sets = cd0\n"
	else:
		print("### no install medium found ###")

	autoseed += "Set name(s) = done\n"
	autoseed += "Location of sets = done\n"
	autoseed += "Continue without verification = yes\n"
	autoseed += "Exit to (S)hell, (H)alt or (R)eboot = S\n"
	with open(tempdir + "/install.conf", "w") as ofile:
		ofile.write(autoseed)

	if hostdata["target"] == "pxe" and "version" in hostdata:
		isolinuxtxtnet = ""
		isolinuxtxtnet += "LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  MENU LABEL Autoinstall: " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  KERNEL pxechn.c32\n"
		isolinuxtxtnet += "  APPEND openbsd6.6/auto_install\n"
		isolinuxtxtnet += "\n"
		with open(tempdir + "/isolinuxtxt.net", "w") as ofile:
			ofile.write(isolinuxtxtnet)
		os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
		os.system("cp " + tempdir + "/install.conf /var/www/html/hosts/" + hostdata["hostid"] + "/install.conf")
		os.system("ln -sf hosts/" + hostdata["hostid"] + "/install.conf /var/www/html/install.conf")
		os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"] + "/services")
		os.system("cp -a " + tempdir + "/services/* /var/www/html/hosts/" + hostdata["hostid"] + "/services/")
		os.system("cat /var/lib/tftpboot/sub.tmpl > /var/lib/tftpboot/autoinstall.conf")
		os.system("cat temp/*/isolinuxtxt.net >> /var/lib/tftpboot/autoinstall.conf")
		for interface in hostdata["network"]["interfaces"]:
			if "ipv4" in hostdata["network"]["interfaces"][interface]:
				for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
					if "hwaddr" in hostdata["network"]["interfaces"][interface]:
						os.system("cat /var/lib/tftpboot/sub.tmpl > /var/lib/tftpboot/pxelinux.cfg/01-" + hostdata["network"]["interfaces"][interface]["hwaddr"].replace(":", "-"))
						os.system("echo \"DEFAULT " + hostdata["hostid"] + "\" >> /var/lib/tftpboot/pxelinux.cfg/01-" + hostdata["network"]["interfaces"][interface]["hwaddr"].replace(":", "-"))
						os.system("cat " + tempdir + "/isolinuxtxt.net >> /var/lib/tftpboot/pxelinux.cfg/01-" + hostdata["network"]["interfaces"][interface]["hwaddr"].replace(":", "-"))



	if "iso" in hostdata:
		if isocheck == True:
			if not os.path.exists(tempdir + "/auto.iso"):
				copy = {
					"/install.conf": [tempdir + "/install.conf", "666", "root"],
					"bsdtools": ["files/openbsd", "666", "root"]
				}
				for service in services:
					if service != "":
						copy["service_" + service.split("/")[-1]] = [tempdir + "/services/" + service.split("/")[-1], "777", "root"]
				mkisofs.mkisofs(
					tempdir,
					hostdata["iso"],
					tempdir + "/auto.iso",
					isoname,
					isoversion + "/" + isoarch + "/cdbr",
					"boot.catalog",
					"-R",
					copy
				)
		else:
			print("ERROR: unknown ISO-Image")
