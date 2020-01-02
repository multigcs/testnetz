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
				print(isoname)
				if "_RELEASE_" in isoname:
					isocheck = True
					isoversion = isoname.split("_")[0] + "." + isoname.split("_")[1]
					isoarch = isoname.split("_")[-2]
	if isocheck == True:
		print("  ISO-Name:    " + isoname)
		print("  ISO-Version: " + isoversion)
		print("  ISO-Arch:    " + isoarch)
	## generate autoseed ##
	autoseed = ""
	autoseed += "# Set up Partitioning\n"
	autoseed += "PARTITIONS=\"ada0 { 5G freebsd-ufs /, 1G freebsd-swap }\"\n"
	autoseed += "\n"
	autoseed += "\n"
	autoseed += "# Which distribution files to install\n"
	autoseed += "DISTRIBUTIONS=\"kernel.txz base.txz ports.txz\"\n"
	autoseed += "\n"
	autoseed += "################\n"
	autoseed += "# Begin Scripting  \n"
	autoseed += "################\n"
	autoseed += "#!/bin/sh\n"
	autoseed += "\n"
	autoseed += "# Set up Networking\n"
	autoseed += "hostname " + hostdata["hostname"] + "\n"
	autoseed += "echo 'hostname=\"" + hostdata["hostname"] + "." + hostdata["domainname"] + "\"' >> /etc/rc.conf\n"
	autoseed += "echo 'nisdomainname=\"" + hostdata["domainname"] + "\"' >> /etc/rc.conf\n"
	dns = ""
	for nameserver in hostdata["network"]["nameservers"]:
		dns = nameserver
		break
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				autoseed += "ifconfig " + interface + " " + ipv4["address"] + " netmask " + ipv4["netmask"] + "\n"
	autoseed += "route add default " + hostdata["network"]["gateway"] + "\n"
	autoseed += "\n"
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				autoseed += "echo \"#" + interface + "=DHCP\" >> /etc/rc.conf\n"
				autoseed += "echo 'ifconfig_" + interface + "=\"inet " + ipv4["address"] + " netmask " + ipv4["netmask"] + "\"' >> /etc/rc.conf\n"
	autoseed += "echo 'defaultrouter=\"" + hostdata["network"]["gateway"] + "\"' >> /etc/rc.conf\n"
	autoseed += "\n"
	autoseed += "echo 'sshd_enable=YES' >> /etc/rc.conf\n"
	autoseed += "echo 'keymap=de.kbd' >> /etc/rc.conf\n"
	autoseed += "\n"
	autoseed += "echo 'search domain " + hostdata["domainname"] + "' > /etc/resolv.conf\n"
	autoseed += "echo 'nameserver " + dns + "' >> /etc/resolv.conf\n"
	autoseed += "\n"
	autoseed += "# Set Time Zone\n"
	autoseed += "/bin/cp /usr/share/zoneinfo/UTC /etc/localtime\n"
	autoseed += "/usr/bin/touch /etc/wall_cmos_clock\n"
	autoseed += "/sbin/adjkerntz -a\n"
	autoseed += "/usr/sbin/ntpdate -u 0.pool.ntp.org\n"
	autoseed += "\n"

	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			autoseed += "#Set Default Root Password\n"
			autoseed += "echo \"" + hostdata["users"][user]["password"] + "\" | pw usermod root -h 0\n"
			autoseed += "\n"
		else:
			userflag = True
			autoseed += "# Add Group " + user + "\n"
			autoseed += "pw groupadd -n " + user + " -g 1001\n"
			autoseed += "\n"
			autoseed += "#Add User " + user + "\n"
			autoseed += "echo \"" + hostdata["users"][user]["password"] + "\" | pw useradd -n \"" + user + "\" -u 1001 -g 1001 -s csh -h 0 \n"
			autoseed += "\n"


	autoseed += "\n"
	autoseed += "#Add Packages\n"
	autoseed += "pkg install -y python\n"
	autoseed += "pkg install -y dmidecode\n"
	autoseed += "pkg install -y wget\n"
	autoseed += "\n"
	autoseed += "\n"
	autoseed += "#Add SSH-Key\n"
	autoseed += "sed \"s|^#PermitRootLogin .*|PermitRootLogin yes|g\" /etc/ssh/sshd_config > /etc/ssh/sshd_config.new\n"
	autoseed += "mv /etc/ssh/sshd_config.new /etc/ssh/sshd_config\n"
	autoseed += "\n"
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			if "sshpubkey" in hostdata["users"][user]:
				autoseed += "mkdir -p /root/.ssh\n"
				autoseed += "chown root:root /root/.ssh\n"
				autoseed += "chmod 700 /root/.ssh\n"
				autoseed += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /root/.ssh/authorized_keys\n"
				autoseed += "chown root:root /root/.ssh/authorized_keys\n"
				autoseed += "chmod 600 /root/.ssh/authorized_keys\n"
				autoseed += "\n"
		elif userflag == False:
			if "sshpubkey" in hostdata["users"][user]:
				autoseed += "mkdir -p /home/" + user + "/.ssh\n"
				autoseed += "chown " + user + ":" + user + " /home/" + user + "/.ssh\n"
				autoseed += "chmod 700 /home/" + user + "/.ssh\n"
				autoseed += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /home/" + user + "/.ssh/authorized_keys\n"
				autoseed += "chown " + user + ":" + user + " /home/" + user + "/.ssh/authorized_keys\n"
				autoseed += "chmod 600 /home/" + user + "/.ssh/authorized_keys\n"
				autoseed += "\n"

	autoseed += "pkg install -y wget\n"
	os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"] + "/services")
	autoseed += "\n"
	for service in services:
		if service != "":
			os.system("cp -a " + tempdir + "/services/* /var/www/html/hosts/" + hostdata["hostid"] + "/services/")
			autoseed += "wget -O /root/service_" + service.split("/")[-1] + " http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/services/" + service.split("/")[-1] + " >> /root/service.log 2>&1\n"
			autoseed += "if test -e /root/service_" + service.split("/")[-1] + "\n"
			autoseed += "then\n"
			autoseed += " sh /root/service_" + service.split("/")[-1] + " 2>&1 | tee -a /root/service_" + service.split("/")[-1] + ".log || true\n"
			autoseed += "fi\n"
			autoseed += "\n"

	autoseed += "\n"
	autoseed += "#Reboot System\n"
	autoseed += "reboot\n"
	with open(tempdir + "/autoseed", "w") as ofile:
		ofile.write(autoseed)


	if hostdata["target"] == "pxe" and "version" in hostdata:
		isolinuxtxtnet = ""
		isolinuxtxtnet += "LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  MENU LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  KERNEL memdisk\n"
		isolinuxtxtnet += "  APPEND initrd=mfsbsd-10.3-RELEASE-amd64.img harddisk raw\n"
		isolinuxtxtnet += "\n"
		with open(tempdir + "/isolinuxtxt.net", "w") as ofile:
			ofile.write(isolinuxtxtnet)

		for rfile in get_files():
			if rfile.startswith("files/freebsd/tftp/"):
				if not os.path.exists(rfile):
					print("  Get missing file: " + rfile + " ...")
					os.system("mkdir -p " + os.path.dirname(rfile))
					os.system("wget -O " + rfile + " " + rfiles[rfile])

		os.system("rm -rf /var/www/html/hosts/" + hostdata["hostid"])
		os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
		os.system("cp " + tempdir + "/autoseed /var/www/html/hosts/" + hostdata["hostid"] + "/install.conf")
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
					"etc/installerconfig": [tempdir + "/autoseed", "666", "root"],
						"bsdtools": ["files/freebsd", "666", "root"]
				}
				for service in services:
					if service != "":
						copy["service_" + service.split("/")[-1]] = [tempdir + "/services/" + service.split("/")[-1], "777", "root"]
				mkisofs.mkisofs(
					tempdir,
					hostdata["iso"],
					tempdir + "/auto.iso",
					"12_0_RELEASE_AMD64_CD",
					"boot/cdboot",
					"",
					"-R",
					copy
				)
		else:
			print("ERROR: unknown ISO-Image")
