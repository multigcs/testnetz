#!/usr/bin/python3
#
#

import os
import json
import mkisofs

# TODO: check autoinstall of services on libvirt/pxe (empty scripts)

mirror_base = "http://ftp.agdsn.de/pub/mirrors"

def get_files():
	files = {}
	## Centos7
	files["isoimages/CentOS-7-x86_64-DVD-1908.iso"] = mirror_base + "/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-1908.iso"
	files["files/centos/tftp/centos-installer-7/vmlinuz"] = mirror_base + "/centos/7/os/x86_64/isolinux/vmlinuz"
	files["files/centos/tftp/centos-installer-7/initrd.img"] = mirror_base + "/centos/7/os/x86_64/isolinux/initrd.img"
	## Centos8
	files["isoimages/CentOS-8-x86_64-1905-dvd1.iso"] = mirror_base + "/centos/8/isos/x86_64/CentOS-8-x86_64-1905-dvd1.iso"
	files["files/centos/tftp/centos-installer-8/vmlinuz"] = mirror_base + "/centos/8/BaseOS/x86_64/kickstart/isolinux/vmlinuz"
	files["files/centos/tftp/centos-installer-8/initrd.img"] = mirror_base + "/centos/8/BaseOS/x86_64/kickstart/isolinux/initrd.img"
	## Fedora30
	files["isoimages/Fedora-Server-dvd-x86_64-30-1.2.iso"] = mirror_base + "/fedora/linux/releases/30/Server/x86_64/iso/Fedora-Server-dvd-x86_64-30-1.2.iso"
	files["files/centos/tftp/fedora-installer-30/vmlinuz"] = mirror_base + "/fedora/linux/releases/30/Server/x86_64/os/isolinux/vmlinuz"
	files["files/centos/tftp/fedora-installer-30/initrd.img"] = mirror_base + "/fedora/linux/releases/30/Server/x86_64/os/isolinux/initrd.img"
	return files


def pxe(bootserver):
	for rfile in get_files():
		if rfile.startswith("files/"):
			if not os.path.exists(rfile):
				print("  Get missing file: " + rfile + " ...")
				os.system("mkdir -p " + os.path.dirname(rfile))
				os.system("wget -O " + rfile + " " + get_files()[rfile])
	os.system("cp -auv files/centos/tftp/* /var/lib/tftpboot/")
	#os.system("cp -auv files/centos/http/* /var/www/html/")
	isolinuxtxtnet = ""
	for version in ["7", "8"]:
		isolinuxtxtnet += "LABEL centos" + version.replace(".", "") + "\n"
		isolinuxtxtnet += "  MENU LABEL Centos-" + version + "\n"
		isolinuxtxtnet += "  KERNEL centos-installer-" + version + "/vmlinuz\n"
		isolinuxtxtnet += "  APPEND initrd=centos-installer-" + version + "/initrd.img ip=dhcp inst.repo=" + mirror_base + "/centos/" + version + "/\n"
		isolinuxtxtnet += "\n"
	for version in ["30"]:
		isolinuxtxtnet += "LABEL fedora" + version.replace(".", "") + "\n"
		isolinuxtxtnet += "  MENU LABEL Fedora-" + version + "\n"
		isolinuxtxtnet += "  KERNEL fedora-installer-" + version + "/vmlinuz\n"
		isolinuxtxtnet += "  APPEND initrd=fedora-installer-" + version + "/initrd.img ip=dhcp inst.repo=" + mirror_base + "/fedora/linux/releases/" + version + "/Server/x86_64/os/\n"
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
				print(isoname)
				if isoname.startswith("CentOS-"):
					isocheck = True
					isoversion = isoname.split("-")[1]
					isoarch = isoname.split("-")[-1]
				elif isoname.startswith("CentOS"):
					isocheck = True
					isoversion = isoname.split(" ")[1]
					isoarch = isoname.split()[-1]
				elif isoname.startswith("Fedora-"):
					isocheck = True
					isoversion = isoname.split("-")[-1]
					isoarch = isoname.split("-")[-2]
	if isocheck == True:
		print("  ISO-Name:    " + isoname)
		print("  ISO-Version: " + isoversion)
		print("  ISO-Arch:    " + isoarch)
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
	setup += "## hostname ##\n"
	setup += "cat \"" + hostdata["hostname"] + "." + hostdata["domainname"] + "\" > /etc/hostname\n"
	setup += "hostname '" + hostdata["hostname"] + "'\n"
	setup += "domainname '" + hostdata["domainname"] + "'\n"
	setup += "\n"
	setup += "## resolv.conf ##\n"
	setup += "cat <<EOF > /etc/resolv.conf\n"
	setup += "search " + hostdata["domainname"] + "\n"
	for nameserver in hostdata["network"]["nameservers"]:
		setup += "nameserver " + nameserver + "\n"
	setup += "EOF\n"
	setup += "\n"
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				setup += "## " + interface + " ##\n"
				setup += "ip a add " + ipv4["address"] + "/" + ipv4["netmask"] + " dev " + interface + "\n"
				setup += "ip route add default via " + hostdata["network"]["gateway"] + "\n"
				setup += "cat <<EOF > /etc/sysconfig/network-scripts/ifcfg-" + interface + "\n"
				setup += "#UUID=\"\"\n"
				setup += "DNS1=\"" + dns + "\"\n"
				setup += "IPADDR=\"" + ipv4["address"] + "\"\n"
				setup += "GATEWAY=\"" + hostdata["network"]["gateway"] + "\"\n"
				setup += "NETMASK=\"" + ipv4["netmask"] + "\"\n"
				setup += "BOOTPROTO=\"static\"\n"
				setup += "DEVICE=\"" + interface + "\"\n"
				setup += "ONBOOT=\"yes\"\n"
				setup += "IPV6INIT=\"yes\"\n"
				setup += "EOF\n"
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
	postsh += "yum install -y python3\n"
	postsh += "\n"
	if "dockerfile" in hostdata:
		script, copy = docker.docker2post(hostdata["dockerfile"], tempdir + "/dockerdata", "/mount/cdrom")
		postsh += "######### DOCKERFILE #########\n"
		postsh += "cp -a /mount/cdrom/dockerdata/* /\n"
		postsh += "##############################\n"
		postsh += script + "\n"
		postsh += "##############################\n"
		postsh += "\n"


	postsh += "yum install -y wget\n"
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
	## generate kickstart file ##
	autoseed = ""
	autoseed += "auth --enableshadow --passalgo=sha512\n"
	if hostdata["target"] != "pxe":
		autoseed += "cdrom\n"
	else:
		if hostdata["os"] == "fedora":
			autoseed += "url --url=\"" + mirror_base + "/fedora/linux/releases/" + hostdata["version"] + "/Server/x86_64/os/\"\n"
		else:
			if hostdata["version"] == "8":
				autoseed += "url --url=\"" + mirror_base + "/centos/" + hostdata["version"] + "/BaseOS/x86_64/kickstart/\"\n"
			else:
				autoseed += "url --url=\"" + mirror_base + "/centos/" + hostdata["version"] + "/\"\n"
	autoseed += "text\n"
	autoseed += "firstboot --enable\n"
	autoseed += "ignoredisk --only-use=vda\n"
	autoseed += "keyboard --vckeymap=de --xlayouts=''\n"
	autoseed += "lang de_DE.UTF-8\n"
	autoseed += "\n"
	autoseed += "# Network information\n"
	autoseed += "network --bootproto=dhcp --ipv6=auto --hostname=" + hostdata["hostname"] + "." + hostdata["domainname"] + " --activate\n"
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				autoseed += "network --onboot=yes --device=" + interface + " --bootproto=static --ip=" + ipv4["address"] + " --netmask=" + ipv4["netmask"] + " --gateway=" + hostdata["network"]["gateway"] + " --nameserver=" + dns + "\n"
				autoseed += "\n"
				break
	autoseed += "\n"
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			autoseed += "## root ##\n"
			autoseed += "rootpw " + hostdata["users"][user]["password"] + "\n"
			autoseed += "\n"
		elif userflag == False:
			userflag = True
			autoseed += "## user " + user + " ##\n"
			autoseed += "user --groups=wheel --name=" + user + " --password=" + hostdata["users"][user]["password"] + " --gecos=\"" + user + "\"\n"
			autoseed += "\n"
	autoseed += "# System services\n"
	autoseed += "services --enabled=\"chronyd\"\n"
	autoseed += "# Do not configure the X Window System\n"
	autoseed += "skipx\n"
	autoseed += "# System timezone\n"
	autoseed += "timezone --utc Europe/Berlin\n"
	autoseed += "# System bootloader configuration\n"
	autoseed += "bootloader --append=\" crashkernel=auto\" --location=mbr --boot-drive=vda\n"
	autoseed += "autopart --type=thinp\n"
	autoseed += "# Partition clearing information\n"
	autoseed += "clearpart --all --initlabel --drives=vda\n"
	autoseed += "\n"
	autoseed += "reboot\n"
	autoseed += "\n"
	autoseed += "%packages\n"
	autoseed += "@core\n"
	autoseed += "chrony\n"
	autoseed += "kexec-tools\n"
	autoseed += "\n"
	autoseed += "%end\n"
	autoseed += "\n"
	autoseed += "%addon com_redhat_kdump --enable\n"
	autoseed += "\n"
	autoseed += "%end\n"
	autoseed += "\n"
	autoseed += "%anaconda\n"
	autoseed += "pwpolicy root --minlen=6 --minquality=1 --notstrict --nochanges --notempty\n"
	autoseed += "pwpolicy user --minlen=6 --minquality=1 --notstrict --nochanges --emptyok\n"
	autoseed += "pwpolicy luks --minlen=6 --minquality=1 --notstrict --nochanges --notempty\n"
	autoseed += "%end\n"
	autoseed += "\n"
	autoseed += "%post\n"
	autoseed += postsh
	autoseed += "%end\n"
	with open(tempdir + "/autoseed", "w") as ofile:
		ofile.write(autoseed)
	isolinuxcfg = ""
	isolinuxcfg += "\n"
	isolinuxcfg += "default vesamenu.c32\n"
	isolinuxcfg += "timeout 5\n"
	isolinuxcfg += "display boot.msg\n"
	isolinuxcfg += "menu clear\n"
	isolinuxcfg += "menu background splash.png\n"
	isolinuxcfg += "menu title " + hostdata["os"] + "\n"
	isolinuxcfg += "menu vshift 8\n"
	isolinuxcfg += "menu rows 18\n"
	isolinuxcfg += "menu margin 8\n"
	isolinuxcfg += "menu helpmsgrow 15\n"
	isolinuxcfg += "menu tabmsgrow 13\n"
	isolinuxcfg += "\n"
	isolinuxcfg += "label kick\n"
	isolinuxcfg += "  menu label ^Kickstart\n"
	isolinuxcfg += "  menu default\n"
	isolinuxcfg += "  kernel vmlinuz\n"
	isolinuxcfg += "  append initrd=initrd.img inst.stage2=hd:LABEL=" + hostdata["os"] + " inst.ks=cdrom:/dev/cdrom:/ks.cfg\n"
	isolinuxcfg += "\n"
	with open(tempdir + "/isolinuxcfg", "w") as ofile:
		ofile.write(isolinuxcfg)


	if hostdata["target"] == "pxe" and "version" in hostdata:
		isolinuxtxtnet = ""
		isolinuxtxtnet += "LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  MENU LABEL Autoinstall: " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  KERNEL " + hostdata["os"] + "-installer-" + hostdata["version"] + "/vmlinuz\n"
		if hostdata["os"] == "fedora":
			isolinuxtxtnet += "  APPEND initrd=" + hostdata["os"] + "-installer-" + hostdata["version"] + "/initrd.img ip=dhcp inst.repo=" + mirror_base + "/fedora/linux/releases/" + hostdata["version"] + "/Server/x86_64/os/ inst.ks=http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/ks.cfg\n"
		else:
			if hostdata["version"] == "8":
				isolinuxtxtnet += "  APPEND initrd=" + hostdata["os"] + "-installer-" + hostdata["version"] + "/initrd.img ip=dhcp inst.repo=" + mirror_base + "/centos/" + hostdata["version"] + "/BaseOS/x86_64/kickstart inst.ks=http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/ks.cfg\n"
			else:
				isolinuxtxtnet += "  APPEND initrd=" + hostdata["os"] + "-installer-" + hostdata["version"] + "/initrd.img ip=dhcp inst.repo=" + mirror_base + "/centos/" + hostdata["version"] + "/ inst.ks=http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/ks.cfg\n"
		isolinuxtxtnet += "\n"
		with open(tempdir + "/isolinuxtxt.net", "w") as ofile:
			ofile.write(isolinuxtxtnet)
		os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
		os.system("cp " + tempdir + "/autoseed /var/www/html/hosts/" + hostdata["hostid"] + "/ks.cfg")
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
	dockerfile += "RUN yum update -y && yum install -y python3 openssh-server xinetd\n"
	dockerfile += "RUN yum update -y && yum install -y iproute net-tools procps\n"
	dockerfile += "\n"
	dockerfile += "COPY postsh /root/post.sh\n"
	dockerfile += "RUN /bin/sh /root/post.sh\n"
	dockerfile += "\n"
	dockerfile += "CMD mkdir -p /var/run/sshd ; /usr/sbin/sshd-keygen ; /usr/sbin/sshd ; /bin/sh\n"
	dockerfile += "\n"
	for service in services:
		if service != "":
			dockerfile += "COPY services/" + service.split("/")[-1] + " /root/service_" + service.split("/")[-1] + "\n"
			dockerfile += "RUN /bin/sh /root/service_" + service.split("/")[-1] + "\n"
			dockerfile += "\n"
	dockerfile += "\n"
	dockerfile += "RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N \"\"\n"
	dockerfile += "RUN echo -e 'xinetd\\n/sbin/sshd\\n/bin/sh' > /init.sh && chmod 777 /init.sh\n"
	dockerfile += "\n"
	dockerfile += "CMD [\"/bin/sh\", \"/init.sh\"]\n"
	dockerfile += "\n"
	with open(tempdir + "/Dockerfile", "w") as ofile:
		ofile.write(dockerfile)
	if "iso" in hostdata:
		if isocheck == True:
			if not os.path.exists(tempdir + "/auto.iso"):
				copy = {
					"ks.cfg": [tempdir + "/autoseed", "666", "root"],
					"isolinux/isolinux.cfg": [tempdir + "/isolinuxcfg", "666", "root"],
					"lintools": ["files/centos", "666", "root"]
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

