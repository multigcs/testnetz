#!/usr/bin/python3
#
#

import os
import json
import mkisofs

# TODO: check autoinstall of services on libvirt/pxe (empty scripts)

mirror_base = "http://download.opensuse.org/distribution"

def get_files():
	files = {}
	files["isoimages/openSUSE-Leap-15.2-DVD-x86_64-Current.iso"] = mirror_base + "/leap/15.2/iso/openSUSE-Leap-15.2-DVD-x86_64-Current.iso"
	files["files/opensuse/tftp/opensuse-installer-15.2/linux"] = mirror_base + "/leap/15.2/repo/oss/boot/x86_64/loader/linux"
	files["files/opensuse/tftp/opensuse-installer-15.2/initrd"] = mirror_base + "/leap/15.2/repo/oss/boot/x86_64/loader/initrd"
	return files


def pxe(bootserver):
	for rfile in get_files():
		if rfile.startswith("files/"):
			if not os.path.exists(rfile):
				print("  Get missing file: " + rfile + " ...")
				os.system("mkdir -p " + os.path.dirname(rfile))
				os.system("wget -O " + rfile + " " + get_files()[rfile])
	os.system("cp -auv files/opensuse/tftp/* /var/lib/tftpboot/")
	#os.system("cp -auv files/opensuse/http/* /var/www/html/")
	isolinuxtxtnet = ""
	for version in ["15.2"]:
		isolinuxtxtnet += "LABEL opensuse" + version.replace(".", "") + "\n"
		isolinuxtxtnet += "  MENU LABEL openSUSE-" + version + "\n"
		isolinuxtxtnet += "  KERNEL opensuse-installer-" + version + "/linux\n"
		isolinuxtxtnet += "  APPEND initrd=opensuse-installer-" + version + "/initrd install=" + mirror_base + "/leap/" + version + "/repo/oss\n"
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
				if isoname.startswith("openSUSE-"):
					isocheck = True
					isoversion = isoname.split("-")[2]
					isoarch = isoname.split("-")[-1].split("_")[0]
	if isocheck == True:
		print("  ISO-Name:    " + isoname)
		print("  ISO-Version: " + isoversion)
		print("  ISO-Arch:    " + isoarch)
	## generate autoseed ##
	autoseed = ""
	autoseed += "<?xml version='1.0'?>\n"
	autoseed += "<!DOCTYPE profile>\n"
	autoseed += "<profile xmlns='http://www.suse.com/1.0/yast2ns' xmlns:config='http://www.suse.com/1.0/configns'>\n"
	autoseed += "    <general>\n"
	autoseed += "        <mode>\n"
	autoseed += "            <confirm config:type='boolean'>false</confirm>\n"
	autoseed += "            <forceboot config:type='boolean'>true</forceboot>\n"
	autoseed += "            <final_reboot config:type='boolean'>false</final_reboot>\n"
	autoseed += "        </mode>\n"
	autoseed += "    </general>\n"
	autoseed += "    <report>\n"
	autoseed += "        <messages>\n"
	autoseed += "            <show config:type='boolean'>false</show>\n"
	autoseed += "            <timeout config:type='integer'>10</timeout>\n"
	autoseed += "            <log config:type='boolean'>true</log>\n"
	autoseed += "        </messages>\n"
	autoseed += "        <warnings>\n"
	autoseed += "            <show config:type='boolean'>false</show>\n"
	autoseed += "            <timeout config:type='integer'>10</timeout>\n"
	autoseed += "            <log config:type='boolean'>true</log>\n"
	autoseed += "        </warnings>\n"
	autoseed += "        <errors>\n"
	autoseed += "            <show config:type='boolean'>false</show>\n"
	autoseed += "            <timeout config:type='integer'>10</timeout>\n"
	autoseed += "            <log config:type='boolean'>true</log>\n"
	autoseed += "        </errors>\n"
	autoseed += "    </report>\n"
	autoseed += "\n"
	autoseed += "    <keyboard>\n"
	autoseed += "        <keymap>german</keymap>\n"
	autoseed += "    </keyboard>\n"
	autoseed += "    <language>\n"
	autoseed += "        <language>de_DE</language>\n"
	autoseed += "        <languages>de_DE</languages>\n"
	autoseed += "    </language>\n"
	autoseed += "    <timezone>\n"
	autoseed += "        <hwclock>UTC</hwclock>\n"
	autoseed += "        <timezone>Europe/Berlin</timezone>\n"
	autoseed += "    </timezone>\n"
	autoseed += "\n"
	autoseed += "    <partitioning config:type='list'>\n"
	autoseed += "        <drive>\n"
	autoseed += "            <device>/dev/vda</device>\n"
	autoseed += "            <initialize config:type='boolean'>true</initialize>\n"
	autoseed += "            <partitions config:type='list'>\n"
	autoseed += "                <partition>\n"
	autoseed += "                    <label>boot</label>\n"
	autoseed += "                    <mount>/boot</mount>\n"
	autoseed += "                    <mountby config:type='symbol'>label</mountby>\n"
	autoseed += "                    <partition_type>primary</partition_type>\n"
	autoseed += "                    <size>200M</size>\n"
	autoseed += "                </partition>\n"
	autoseed += "                <partition>\n"
	autoseed += "                    <label>system</label>\n"
	autoseed += "                    <lvm_group>system</lvm_group>\n"
	autoseed += "                    <partition_type>primary</partition_type>\n"
	autoseed += "                    <size>max</size>\n"
	autoseed += "                </partition>\n"
	autoseed += "            </partitions>\n"
	autoseed += "            <use>all</use>\n"
	autoseed += "        </drive>\n"
	autoseed += "        <drive>\n"
	autoseed += "            <device>/dev/system</device>\n"
	autoseed += "            <initialize config:type='boolean'>true</initialize>\n"
	autoseed += "            <is_lvm_vg config:type='boolean'>true</is_lvm_vg>\n"
	autoseed += "            <partitions config:type='list'>\n"
	autoseed += "                <partition>\n"
	autoseed += "                    <label>swap</label>\n"
	autoseed += "                    <mountby config:type='symbol'>label</mountby>\n"
	autoseed += "                    <filesystem config:type='symbol'>swap</filesystem>\n"
	autoseed += "                    <lv_name>swap</lv_name>\n"
	autoseed += "                    <mount>swap</mount>\n"
	autoseed += "                    <size>2G</size>\n"
	autoseed += "                </partition>\n"
	autoseed += "                <partition>\n"
	autoseed += "                    <label>root</label>\n"
	autoseed += "                    <mountby config:type='symbol'>label</mountby>\n"
	autoseed += "                    <filesystem config:type='symbol'>ext4</filesystem>\n"
	autoseed += "                    <lv_name>root</lv_name>\n"
	autoseed += "                    <mount>/</mount>\n"
	autoseed += "                    <size>max</size>\n"
	autoseed += "                </partition>\n"
	autoseed += "            </partitions>\n"
	autoseed += "            <pesize>4M</pesize>\n"
	autoseed += "            <type config:type='symbol'>CT_LVM</type>\n"
	autoseed += "            <use>all</use>\n"
	autoseed += "        </drive>\n"
	autoseed += "    </partitioning>\n"
	autoseed += "\n"
	autoseed += "    <bootloader>\n"
	autoseed += "        <loader_type>grub2</loader_type>\n"
	autoseed += "    </bootloader>\n"

	autoseed += "    <networking>\n"
	autoseed += "        <ipv6 config:type='boolean'>false</ipv6>\n"
	autoseed += "        <keep_install_network config:type='boolean'>true</keep_install_network>\n"


	autoseed += "    <dns>\n"
	autoseed += "      <dhcp_hostname config:type='boolean'>false</dhcp_hostname>\n"
	autoseed += "      <hostname>" + hostdata["hostname"] + "</hostname>\n"
	autoseed += "      <domain>" + hostdata["domainname"] + "</domain>\n"
	autoseed += "      <nameservers config:type='list'>\n"
	for nameserver in hostdata["network"]["nameservers"]:
		autoseed += "        <nameserver>" + nameserver + "</nameserver>\n"
	autoseed += "      </nameservers>\n"
	autoseed += "      <resolv_conf_policy>auto</resolv_conf_policy>\n"
	autoseed += "      <searchlist config:type='list'>\n"
	autoseed += "        <search>" + hostdata["domainname"] + "</search>\n"
	autoseed += "      </searchlist>\n"
	autoseed += "      <write_hostname config:type='boolean'>false</write_hostname>\n"
	autoseed += "    </dns>\n"

	iface = ""
	autoseed += "        <interfaces config:type='list'>\n"
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				if iface == "":
					iface = interface
				autoseed += "            <interface>\n"
				autoseed += "                <device>" + interface + "</device>\n"
#				autoseed += "                <bootproto>dhcp</bootproto>\n"
				autoseed += "                <bootproto>static</bootproto>\n"
				autoseed += "                <ipaddr>" + ipv4["address"] + "</ipaddr>\n"
				autoseed += "                <netmask>" + ipv4["netmask"] + "</netmask>\n"
				autoseed += "                <firewall>no</firewall>\n"
				autoseed += "                <startmode>onboot</startmode>\n"
				autoseed += "            </interface>\n"
	autoseed += "        </interfaces>\n"

	autoseed += "      <routing>\n"
	autoseed += "        <ipv4_forward config:type='boolean'>true</ipv4_forward>\n"
	autoseed += "        <ipv6_forward config:type='boolean'>false</ipv6_forward>\n"
	autoseed += "        <routes config:type='list'>\n"
	autoseed += "          <route>\n"
	autoseed += "            <destination>default</destination>\n"
	autoseed += "            <device>" + iface + "</device>\n"
	autoseed += "            <gateway>" + hostdata["network"]["gateway"] + "</gateway>\n"
	autoseed += "            <netmask>-</netmask>\n"
	autoseed += "          </route>\n"
	autoseed += "        </routes>\n"
	autoseed += "      </routing>\n"
	autoseed += "    </networking>\n"

	autoseed += "    <firewall>\n"
	autoseed += "        <enable_firewall config:type='boolean'>false</enable_firewall>\n"
	autoseed += "        <start_firewall config:type='boolean'>false</start_firewall>\n"
	autoseed += "    </firewall>\n"

	autoseed += "    <software>\n"
	autoseed += "        <image/>\n"
	autoseed += "        <instsource>" + mirror_base + "/15.1/repo/oss/</instsource>\n"
	autoseed += "        <do_online_update config:type='boolean'>true</do_online_update>\n"
	autoseed += "        <kernel>kernel-default</kernel>\n"
	autoseed += "        <patterns config:type='list'>\n"
	autoseed += "            <pattern>base</pattern>\n"
	autoseed += "        </patterns>\n"
	autoseed += "        <packages config:type='list'>\n"
	autoseed += "            <package>kernel-default-devel</package>\n"
	autoseed += "            <package>gcc</package>\n"
	autoseed += "            <package>glibc-locale</package>\n"
	autoseed += "            <package>grub2</package>\n"
	autoseed += "            <package>make</package>\n"
	autoseed += "            <package>iproute2</package>\n"
	autoseed += "            <package>ntp</package>\n"
	autoseed += "            <package>openssh</package>\n"
	autoseed += "            <package>procps</package>\n"
	autoseed += "            <package>sudo</package>\n"
	autoseed += "            <package>vim-data</package>\n"
	autoseed += "            <package>yast2-hardware-detection</package>\n"
	autoseed += "            <package>yast2-runlevel</package>\n"
	autoseed += "            <package>yast2-users</package>\n"
	autoseed += "            <package>zypper</package>\n"
	autoseed += "            <package>bash</package>\n"
	autoseed += "            <package>puppet</package>\n"
	autoseed += "            <package>autoyast2-installation</package>\n"
	autoseed += "            <package>autoyast2</package>\n"
	autoseed += "            <package>bundle-lang-common-en</package>\n"
	autoseed += "            <package>yast2-installation</package>\n"
	autoseed += "            <package>yast2-network</package>\n"
	autoseed += "            <package>yast2-theme-openSUSE</package>\n"
	autoseed += "            <package>wget</package>\n"
	autoseed += "        </packages>\n"
	autoseed += "        <remove-packages config:type='list'>\n"
	autoseed += "            <package>virtualbox-guest-kmp-default</package>\n"
	autoseed += "            <package>virtualbox-guest-tools</package>\n"
	autoseed += "        </remove-packages>\n"
	autoseed += "    </software>\n"

	autoseed += "    <runlevel>\n"
	autoseed += "        <default>3</default>\n"
	autoseed += "        <services config:type='list'>\n"
	autoseed += "            <service>\n"
	autoseed += "                <service_name>ntp</service_name>\n"
	autoseed += "                <service_status>enable</service_status>\n"
	autoseed += "            </service>\n"
	autoseed += "            <service>\n"
	autoseed += "                <service_name>sshd</service_name>\n"
	autoseed += "                <service_status>enable</service_status>\n"
	autoseed += "            </service>\n"
	autoseed += "        </services>\n"
	autoseed += "    </runlevel>\n"

	autoseed += "    <groups config:type='list'>\n"
	autoseed += "        <group>\n"
	autoseed += "            <gid>100</gid>\n"
	autoseed += "            <groupname>users</groupname>\n"
	autoseed += "            <userlist/>\n"
	autoseed += "        </group>\n"
	autoseed += "    </groups>\n"

	autoseed += "    <user_defaults>\n"
	autoseed += "        <expire/>\n"
	autoseed += "        <group>100</group>\n"
	autoseed += "        <groups/>\n"
	autoseed += "        <home>/home</home>\n"
	autoseed += "        <inactive>-1</inactive>\n"
	autoseed += "        <no_groups config:type='boolean'>true</no_groups>\n"
	autoseed += "        <shell>/bin/bash</shell>\n"
	autoseed += "        <skel>/etc/skel</skel>\n"
	autoseed += "        <umask>022</umask>\n"
	autoseed += "    </user_defaults>\n"

	autoseed += "    <users config:type='list'>\n"
	userflag = False
	for user in hostdata["users"]:
		if user == "root":
			autoseed += "        <user>\n"
			autoseed += "            <user_password>" + hostdata["users"][user]["password"] + "</user_password>\n"
			autoseed += "            <username>root</username>\n"
			autoseed += "        </user>\n"
		elif userflag == False:
			userflag = True
			autoseed += "        <user>\n"
			autoseed += "            <fullname>" + user + "</fullname>\n"
			autoseed += "            <gid>100</gid>\n"
			autoseed += "            <home>/home/" + user + "</home>\n"
			autoseed += "            <password_settings>\n"
			autoseed += "                <expire/>\n"
			autoseed += "                <flag/>\n"
			autoseed += "                <inact>-1</inact>\n"
			autoseed += "                <max>99999</max>\n"
			autoseed += "                <min>0</min>\n"
			autoseed += "                <warn>7</warn>\n"
			autoseed += "            </password_settings>\n"
			autoseed += "            <shell>/bin/bash</shell>\n"
			autoseed += "            <uid>1000</uid>\n"
			autoseed += "            <user_password>" + hostdata["users"][user]["password"] + "</user_password>\n"
			autoseed += "            <username>" + user + "</username>\n"
			autoseed += "        </user>\n"
	autoseed += "    </users>\n"


	autoseed += "    <scripts>\n"
	autoseed += "        <chroot-scripts config:type='list'>\n"
	autoseed += "            <script>\n"
	autoseed += "                <chrooted config:type='boolean'>true</chrooted>\n"
	autoseed += "                <filename>chroot.sh</filename>\n"
	autoseed += "                <interpreter>shell</interpreter>\n"
	autoseed += "                <source><![CDATA[\n"
	autoseed += "#!/bin/sh\n"
	autoseed += "sed -i \"s|^#PermitRootLogin .*|PermitRootLogin yes|g\" /etc/ssh/sshd_config\n"
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


	autoseed += "zypper install -y wget\n"
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

	autoseed += "]]>\n"
	autoseed += "                </source>\n"
	autoseed += "            </script>\n"
	autoseed += "        </chroot-scripts>\n"
	autoseed += "    </scripts>\n"


	autoseed += "    <kdump>\n"
	autoseed += "        <add_crash_kernel config:type='boolean'>false</add_crash_kernel>\n"
	autoseed += "    </kdump>\n"
	autoseed += "</profile>\n"
	with open(tempdir + "/autoseed", "w") as ofile:
		ofile.write(autoseed)

	isolinuxtxt = ""
	isolinuxcfg = ""
	isolinuxcfg += "\n"
	isolinuxtxt += "default linux\n"
	isolinuxtxt += "\n"
	isolinuxtxt += "# install\n"
	isolinuxtxt += "label linux\n"
	isolinuxtxt += "  kernel linux\n"
	isolinuxtxt += "  append initrd=initrd autoyast=file:///autoinstall.xml showopts\n"
	isolinuxtxt += "\n"
	isolinuxtxt += "ui		gfxboot bootlogo message\n"
	isolinuxtxt += "implicit	1\n"
	isolinuxtxt += "prompt		1\n"
	isolinuxtxt += "timeout		60\n"
	isolinuxtxt += "\n"
	with open(tempdir + "/isolinuxtxt", "w") as ofile:
		ofile.write(isolinuxtxt)


	if hostdata["target"] == "pxe" and "version" in hostdata:
		isolinuxtxtnet = ""
		isolinuxtxtnet += "LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  MENU LABEL " + hostdata["hostid"] + "\n"
		isolinuxtxtnet += "  KERNEL " + hostdata["os"] + "-installer-" + hostdata["version"] + "/linux\n"
		isolinuxtxtnet += "  APPEND initrd=" + hostdata["os"] + "-installer-" + hostdata["version"] + "/initrd autoyast=http://" + hostdata["bootserver"] + "/hosts/" + hostdata["hostid"] + "/autoinstall.xml install=" + mirror_base + "/leap/" + hostdata["version"] + "/repo/oss\n"
		isolinuxtxtnet += "\n"
		with open(tempdir + "/isolinuxtxt.net", "w") as ofile:
			ofile.write(isolinuxtxtnet)
		os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
		os.system("cp " + tempdir + "/autoseed /var/www/html/hosts/" + hostdata["hostid"] + "/autoinstall.xml")
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
		dockerfile += "FROM opensuse:" + hostdata["version"] + "\n"
	else:
		dockerfile += "FROM opensuse\n"
	dockerfile += "\n"
	dockerfile += "RUN yum update -y && yum install -y python36 openssh-server xinetd\n"
	dockerfile += "RUN yum update -y && yum install -y iproute net-tools\n"
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
					"autoinstall.xml": [tempdir + "/autoseed", "444", "root"],
					"boot/x86_64/loader/isolinux.cfg": [tempdir + "/isolinuxtxt", "444", "root"],
					"lintools": ["files/opensuse", "666", "root"]
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
					"openSUSE-Leap-15.1-DVD-x86_64470",
					"boot/x86_64/loader/isolinux.bin",
					"",
					"-D -r -l -boot-load-size 4 -boot-info-table -input-charset utf-8",
					copy
				)
		else:
			print("ERROR: unknown ISO-Image")



