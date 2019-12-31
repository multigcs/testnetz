#!/usr/bin/python3
#
#

import os
import json
import mkisofs


def get_files():
	files = {}
	## Debian10
	files["isoimages/debian-10.2.0-amd64-netinst.iso"] = "http://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-10.2.0-amd64-netinst.iso"
	files["files/ubuntu/tftp/debian-installer-10/linux"] = "http://ftp.debian.org/debian/dists/Debian10.2/main/installer-amd64/current/images/netboot/debian-installer/amd64/linux"
	files["files/ubuntu/tftp/debian-installer-10/initrd.gz"] = "http://ftp.debian.org/debian/dists/Debian10.2/main/installer-amd64/current/images/netboot/debian-installer/amd64/initrd.gz"
	## Ubuntu1804
	files["isoimages/ubuntu-18.04.3-server-amd64.iso"] = "http://cdimage.ubuntu.com/releases/ubuntu-18.04.3-server-amd64.iso"
	files["files/ubuntu/tftp/ubuntu-installer-18.04/linux"] = "http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/linux"
	files["files/ubuntu/tftp/ubuntu-installer-18.04/initrd.gz"] = "http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/initrd.gz"
	## Ubuntu1910
	files["isoimages/ubuntu-19.10-server-amd64.iso"] = "http://cdimage.ubuntu.com/releases/19.10/release/ubuntu-19.10-server-amd64.iso"
	files["files/ubuntu/tftp/ubuntu-installer-19.10/linux"] = "http://archive.ubuntu.com/ubuntu/dists/eoan/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/linux"
	files["files/ubuntu/tftp/ubuntu-installer-19.10/initrd.gz"] = "http://archive.ubuntu.com/ubuntu/dists/eoan/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/initrd.gz"
	return files


def pxe(bootserver):
	for rfile in get_files():
		if rfile.startswith("files/"):
			if not os.path.exists(rfile):
				print("  Get missing file: " + rfile + " ...")
				os.system("mkdir -p " + os.path.dirname(rfile))
				os.system("wget -O " + rfile + " " + get_files()[rfile])
	os.system("cp -auv files/ubuntu/tftp/* /var/lib/tftpboot/")
	#os.system("cp -auv files/ubuntu/http/* /var/www/html/")
	isolinuxtxtnet = ""
	for version in ["10"]:
		isolinuxtxtnet += "LABEL debian" + version.replace(".", "") + "\n"
		isolinuxtxtnet += "  MENU LABEL Debian-" + version + "\n"
		isolinuxtxtnet += "  KERNEL debian-installer-" + version + "/linux\n"
		isolinuxtxtnet += "  APPEND initrd=debian-installer-" + version + "/initrd.gz\n"
		isolinuxtxtnet += "\n"
	for version in ["18.04", "19.10"]:
		isolinuxtxtnet += "LABEL ubuntu" + version.replace(".", "") + "\n"
		isolinuxtxtnet += "  MENU LABEL Ubuntu-" + version + "\n"
		isolinuxtxtnet += "  KERNEL ubuntu-installer-" + version + "/linux\n"
		isolinuxtxtnet += "  APPEND initrd=ubuntu-installer-" + version + "/initrd.gz\n"
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
				if isoname.startswith("Ubuntu"):
					isocheck = True
					isoversion = isoname.split()[1]
					isoarch = isoname.split()[-1]
				elif isoname.startswith("Debian"):
					isocheck = True
					isoversion = isoname.split()[1]
					isoarch = isoname.split()[-2]
	if isocheck == True:
		print("  ISO-Name:    " + isoname)
		print("  ISO-Version: " + isoversion)
		print("  ISO-Arch:    " + isoarch)
	## generate setup script ##
	setup = "#!/bin/sh\n"
	setup += "\n"
	setup += "## hostname ##\n"
	setup += "cat \"" + hostdata["hostname"] + "\" > /etc/hostname\n"
	setup += "hostname '" + hostdata["hostname"] + "'\n"
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
	setup += "## interfaces ##\n"
	setup += "cat <<EOF > /etc/network/interfaces"
	setup += "\n"
	setup += "source /etc/network/interfaces.d/*\n"
	setup += "\n"
	setup += "# The loopback network interface\n"
	setup += "auto lo\n"
	setup += "iface lo inet loopback\n"
	setup += "\n"
	setup += "EOF\n"
	setup += "\n"
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				setup += "## interface: " + interface + " ##\n"
				setup += "ip a add " + ipv4["address"] + "/" + ipv4["netmask"] + " dev " + interface + "\n"
				setup += "ip route add default via " + hostdata["network"]["gateway"] + "\n"
				setup += "cat <<EOF >> /etc/network/interfaces"
				setup += "auto " + interface + "\n"
				setup += "iface ens3 inet static\n"
				setup += "	address " + ipv4["address"] + "\n"
				setup += "	netmask " + ipv4["netmask"] + "\n"
				setup += "	gateway " + hostdata["network"]["gateway"] + "\n"
				setup += "	dns-nameservers " + dns + "\n"
				setup += "	dns-search " + hostdata["domainname"] + "\n"
				setup += "\n"
				setup += "EOF\n"
				setup += "\n"
	with open(tempdir + "/setup.sh", "w") as ofile:
		ofile.write(setup)

	autoseed = ""
	autoseed += "## general ##\n"
	autoseed += "d-i auto-install/enable boolean true\n"
	autoseed += "d-i debconf/priority string critical\n"
	autoseed += "d-i pkgsel/update-policy select none\n"
	autoseed += "d-i popularity-contest/participate	boolean	false\n"
	autoseed += "d-i pkgsel/include string openssh-server\n"
	autoseed += "\n"
	autoseed += "\n"
	autoseed += "## Lang ##\n"
	autoseed += "d-i pkgsel/install-language-support boolean false\n"
	autoseed += "d-i debian-installer/language string de\n"
	autoseed += "d-i debian-installer/country string DE\n"
	autoseed += "d-i debian-installer/locale string de_DE\n"
	autoseed += "d-i console-setup/ask_detect boolean false\n"
	autoseed += "d-i keyboard-configuration/xkb-keymap select DE\n"
	autoseed += "\n"
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			autoseed += "## root ##\n"
			autoseed += "d-i passwd/root-login boolean true\n"
			autoseed += "d-i passwd/root-password password " + hostdata["users"][user]["password"] + "\n"
			autoseed += "d-i passwd/root-password-again password " + hostdata["users"][user]["password"] + "\n"
			autoseed += "d-i user-setup/allow-password-weak boolean true\n"
			autoseed += "\n"
		elif userflag == False:
			userflag = True
			autoseed += "## user " + user + " ##\n"
			autoseed += "d-i passwd/make-user boolean true\n"
			autoseed += "d-i passwd/username string " + user + "\n"
			autoseed += "d-i passwd/user-fullname string " + user + "\n"
			autoseed += "d-i passwd/user-password password " + hostdata["users"][user]["password"] + "\n"
			autoseed += "d-i passwd/user-password-again password " + hostdata["users"][user]["password"] + "\n"
			autoseed += "d-i user-setup/allow-password-weak boolean true\n"
			autoseed += "\n"
		else:
			print("## WARNING: only one extra user is allowed ##")
	if userflag == False:
		autoseed += "d-i passwd/make-user boolean false\n"
	autoseed += "## hostname and domainname ##\n"
	autoseed += "d-i netcfg/get_hostname string " + hostdata["hostname"] + "\n"
	autoseed += "d-i netcfg/get_hostname seen true\n"
	autoseed += "d-i netcfg/get_domain string " + hostdata["domainname"] + "\n"
	autoseed += "d-i netcfg/get_domain seen true\n"
	autoseed += "\n"
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			autoseed += "## first network-interface ##\n"
			autoseed += "d-i netcfg/choose_interface select " + interface + "\n"
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				autoseed += "d-i netcfg/disable_dhcp boolean true\n"
				autoseed += "d-i netcfg/confirm_static boolean true\n"
				autoseed += "d-i netcfg/get_ipaddress string " + ipv4["address"] + "\n"
				autoseed += "d-i netcfg/get_netmask string " + ipv4["netmask"] + "\n"
				autoseed += "\n"
			break
	if "gateway" in hostdata["network"]:
		autoseed += "## network-default-gateway ##\n"
		autoseed += "d-i netcfg/get_gateway string " + hostdata["network"]["gateway"] + "\n"
		autoseed += "\n"
	autoseed += "## network-get_nameservers ##\n"
	for nameserver in hostdata["network"]["nameservers"]:
		autoseed += "d-i netcfg/get_nameservers string " + nameserver + "\n"
		break
	autoseed += "\n"
	autoseed += "## disks ##\n"
	autoseed += "d-i partman-auto/disk string /dev/vda\n"
	autoseed += "d-i partman-auto/method string regular\n"
	autoseed += "d-i partman-lvm/device_remove_lvm boolean true\n"
	autoseed += "d-i partman-md/device_remove_md boolean true\n"
	autoseed += "d-i partman-lvm/confirm boolean true\n"
	autoseed += "d-i partman/alignment string \"optimal\"\n"
	autoseed += "d-i partman-auto/expert_recipe string                         \\\n"
	autoseed += "      boot-root ::                                            \\\n"
	autoseed += "              65536 1 -1 ext4                                 \\\n"
	autoseed += "                      $primary{ } $bootable{ }                \\\n"
	autoseed += "                      method{ format } format{ }              \\\n"
	autoseed += "                      use_filesystem{ } filesystem{ ext4 }    \\\n"
	autoseed += "                      mountpoint{ / }                         \\\n"
	autoseed += "              .                                               \\\n"
	autoseed += "              65536 65536 65536 linux-swap                    \\\n"
	autoseed += "                      $primary{ }                             \\\n"
	autoseed += "                      method{ swap } format{ }                \\\n"
	autoseed += "\n"
	autoseed += "d-i partman/confirm_write_new_label boolean true\n"
	autoseed += "d-i partman/choose_partition select finish\n"
	autoseed += "d-i partman/confirm boolean true\n"
	autoseed += "d-i partman/confirm_nooverwrite boolean true\n"
	autoseed += "\n"
	autoseed += "## post-script ##\n"
	if hostdata["target"] == "pxe" and "version" in hostdata:
		autoseed += "d-i preseed/late_command string in-target wget -O /root/post.sh http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/post.sh; in-target /bin/sh /root/post.sh\n"
	else:
		autoseed += "d-i preseed/late_command string in-target /bin/sh /media/cdrom/post.sh\n"
	autoseed += "\n"
	autoseed += "## bootloader ##\n"
	autoseed += "d-i debian-installer/quiet	boolean false\n"
	autoseed += "d-i debian-installer/splash boolean false\n"
	autoseed += "d-i grub-installer/timeout	string 2\n"
	autoseed += "d-i grub-installer/bootdev string /dev/vda\n"
	autoseed += "\n"
	autoseed += "## finish ##\n"
	autoseed += "d-i cdrom-detect/eject boolean true\n"
	autoseed += "d-i finish-install/reboot_in_progress note\n"
	autoseed += "\n"

	with open(tempdir + "/autoseed", "w") as ofile:
		ofile.write(autoseed)
	md5autoseed = os.popen("md5sum " + tempdir + "/autoseed").read().split()[0]

	postsh = ""
	postsh += "#!/bin/sh\n"
	postsh += "\n"
	postsh += "## sshd_config ##\n"
	postsh += "sed -i \"s|^#PermitRootLogin .*|PermitRootLogin yes|g\" /etc/ssh/sshd_config\n"
	postsh += "\n"
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			if "sshpubkey" in hostdata["users"][user]:
				postsh += "## authorized_keys (" + user + ") ##\n"
				postsh += "mkdir -p /root/.ssh\n"
				postsh += "chown root:root /root/.ssh\n"
				postsh += "chmod 700 /root/.ssh\n"
				postsh += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /root/.ssh/authorized_keys\n"
				postsh += "chown root:root /root/.ssh/authorized_keys\n"
				postsh += "chmod 600 /root/.ssh/authorized_keys\n"
				postsh += "\n"
		else:
			postsh += "## add user (" + user + ") ##\n"
			postsh += "useradd " + user + "\n"
			postsh += "echo -e \"" + hostdata["users"][user]["password"] + "\\n" + hostdata["users"][user]["password"] + "\\n\" | passwd " + user + "\n"
			postsh += "\n"
			if "sshpubkey" in hostdata["users"][user]:
				postsh += "## authorized_keys (" + user + ") ##\n"
				postsh += "mkdir -p /home/" + user + "/.ssh\n"
				postsh += "chown " + user + ":" + user + " /home/" + user + "/.ssh\n"
				postsh += "chmod 700 /home/" + user + "/.ssh\n"
				postsh += "echo \"" + hostdata["users"][user]["sshpubkey"] + "\" >> /home/" + user + "/.ssh/authorized_keys\n"
				postsh += "chown " + user + ":" + user + " /home/" + user + "/.ssh/authorized_keys\n"
				postsh += "chmod 600 /home/" + user + "/.ssh/authorized_keys\n"
				postsh += "\n"
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
	if "dockerfile" in hostdata:
		script, copy = docker.docker2post(hostdata["dockerfile"], tempdir + "/dockerdata", "/mount/cdrom")
		postsh += "######### DOCKERFILE #########\n"
		postsh += "cp -a /mount/cdrom/dockerdata/* /\n"
		postsh += "##############################\n"
		postsh += script + "\n"
		postsh += "##############################\n"
		postsh += "\n"
		for cline in copy.split("\n"):
			os.system(cline)

	postsh += "apt-get install -y wget\n"
	os.system("rm -rf /var/www/html/hosts/" + hostdata["hostid"] + "/")
	os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"] + "/services")
	postsh += "\n"
	for service in services:
		if service != "":
			os.system("cp -a " + tempdir + "/services/* /var/www/html/hosts/" + hostdata["hostid"] + "/services/")
			postsh += "wget -O /root/service_" + service.split("/")[-1] + " http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/services/" + service.split("/")[-1] + " >> /root/service.log 2>&1\n"
			postsh += "if test -e /root/service_" + service.split("/")[-1] + "\n"
			postsh += "then\n"
			postsh += " sh /root/service_" + service.split("/")[-1] + " 2>&1 | tee -a /root/service_" + service.split("/")[-1] + ".log || true\n"
			postsh += "fi\n"
			postsh += "\n"

	with open(tempdir + "/postsh", "w") as ofile:
		ofile.write(postsh)
	os.system("cp -a " + tempdir + "/postsh /var/www/html/hosts/" + hostdata["hostid"] + "/post.sh")


	isolinuxtxt = ""
	isolinuxtxt += "default autoinstall\n"
	isolinuxtxt += "label autoinstall\n"
	isolinuxtxt += "  menu label ^Automatically install " + hostdata["os"] + "\n"
	isolinuxtxt += "  menu default\n"
	if hostdata["os"] == "debian":
		isolinuxtxt += "  kernel /install.amd/vmlinuz\n"
		isolinuxtxt += "  append initrd=/install.amd/initrd.gz file=/cdrom/auto.seed debian-installer/locale=de_DE console-setup/layoutcode=de auto=true auto-install/enable=true --\n"
	else:
		isolinuxtxt += "  kernel /install/vmlinuz\n"
		isolinuxtxt += "  append initrd=/install/initrd.gz preseed/file=/cdrom/auto.seed file=/cdrom/auto.seed debian-installer/locale=de_DE console-setup/layoutcode=de auto=true auto-install/enable=true --\n"
	isolinuxtxt += "\n"
	isolinuxtxt += "label hdd\n"
	isolinuxtxt += "  menu label ^Boot from first Harddisk\n"
	isolinuxtxt += "  localboot 0x80\n"
	isolinuxtxt += "\n"
	with open(tempdir + "/isolinuxtxt", "w") as ofile:
		ofile.write(isolinuxtxt)





	if hostdata["target"] == "pxe" and "version" in hostdata:
		isolinuxtxtnet = ""
		isolinuxtxtnet += "LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  MENU LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  KERNEL " + hostdata["os"] + "-installer-" + hostdata["version"] + "/linux\n"
		isolinuxtxtnet += "  APPEND priority=critical initrd=" + hostdata["os"] + "-installer-" + hostdata["version"] + "/initrd.gz url=http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/auto.seed debian-installer/locale=de_DE console-setup/layoutcode=de auto=true auto-install/enable=true --\n"
		isolinuxtxtnet += "\n"
		with open(tempdir + "/isolinuxtxt.net", "w") as ofile:
			ofile.write(isolinuxtxtnet)
		os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
		os.system("cp " + tempdir + "/autoseed /var/www/html/hosts/" + hostdata["hostid"] + "/auto.seed")
		os.system("cat /var/lib/tftpboot/sub.tmpl > /var/lib/tftpboot/autoinstall.conf")
		os.system("cat temp/*/isolinuxtxt.net >> /var/lib/tftpboot/autoinstall.conf")
		for interface in hostdata["network"]["interfaces"]:
			if "ipv4" in hostdata["network"]["interfaces"][interface]:
				for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
					if "hwaddr" in hostdata["network"]["interfaces"][interface]:
						os.system("cat /var/lib/tftpboot/sub.tmpl > /var/lib/tftpboot/pxelinux.cfg/01-" + hostdata["network"]["interfaces"][interface]["hwaddr"].replace(":", "-"))
						os.system("echo \"DEFAULT " + hostdata["hostid"] + "\" >> /var/lib/tftpboot/pxelinux.cfg/01-" + hostdata["network"]["interfaces"][interface]["hwaddr"].replace(":", "-"))
						os.system("cat " + tempdir + "/isolinuxtxt.net >> /var/lib/tftpboot/pxelinux.cfg/01-" + hostdata["network"]["interfaces"][interface]["hwaddr"].replace(":", "-"))




	dockerfile = "\n"
	if "version" in hostdata:
		dockerfile += "FROM " + hostdata["os"] + ":" + hostdata["version"] + "\n"
	else:
		dockerfile += "FROM " + hostdata["os"] + "\n"
	dockerfile += "\n"
	dockerfile += "RUN apt-get update && apt-get -y install iproute2 net-tools iputils-ping\n"
	dockerfile += "RUN apt-get update && apt-get -y install python3 openssh-server xinetd\n"
	dockerfile += "\n"
	dockerfile += "COPY postsh /root/post.sh\n"
	dockerfile += "RUN /bin/sh /root/post.sh\n"
	dockerfile += "\n"
	dockerfile += "CMD mkdir -p /var/run/sshd ; /usr/sbin/sshd ; /bin/sh\n"
	dockerfile += "\n"
	for service in services:
		if service != "":
			dockerfile += "COPY services/" + service.split("/")[-1] + " /root/service_" + service.split("/")[-1] + "\n"
			dockerfile += "RUN /bin/sh /root/service_" + service.split("/")[-1] + " 2>&1 | tee -a /root/service_" + service.split("/")[-1] + ".log\n"
			dockerfile += "\n"
	dockerfile += "\n"
	dockerfile += "RUN echo '/etc/init.d/xinetd restart\\n/etc/init.d/ssh restart\\n/bin/sh' > /init.sh && chmod 777 /init.sh\n"
	dockerfile += "\n"
	dockerfile += "CMD [\"/bin/sh\", \"/init.sh\"]\n"
	dockerfile += "\n"


	with open(tempdir + "/Dockerfile", "w") as ofile:
		ofile.write(dockerfile)
	if "iso" in hostdata:
		if isocheck == True:
			if not os.path.exists(tempdir + "/auto.iso"):
				copy = {
					"auto.seed": [tempdir + "/autoseed", "444", "root"],
					"isolinux/txt.cfg": [tempdir + "/isolinuxtxt", "444", "root"],
					"post.sh": [tempdir + "/postsh", "777", "root"],
					"lintools": ["files/ubuntu", "666", "root"]
				}
				for service in services:
					if service != "":
						copy["service_" + service.split("/")[-1]] = [tempdir + "/services/" + service.split("/")[-1], "777", "root"]
				if "dockerfile" in hostdata:
					copy["dockerdata"] = tempdir + "/dockerdata"
				mkisofs.mkisofs(
					tempdir,
					hostdata["iso"],
					tempdir + "/auto.iso",
					isoname,
					"isolinux/isolinux.bin",
					"isolinux/boot.cat",
					"-D -r -l -boot-load-size 4 -boot-info-table -input-charset utf-8",
					copy
				)
		else:
			print("ERROR: unknown ISO-Image")

