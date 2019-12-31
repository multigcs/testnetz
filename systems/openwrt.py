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
	packages = ["http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/base/zlib_1.2.11-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-base_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/libffi_3.2.1-3_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/base/libbz2_1.0.6-4_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-light_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-ctypes_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-pydoc_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-multiprocessing_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-logging_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-codecs_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/libsqlite3_3260000-4_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-sqlite3_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/libgdbm_1.11-1_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-gdbm_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-email_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-distutils_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/base/libopenssl_1.0.2s-1_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-openssl_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/libexpat_2.2.5-1_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-xml_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-compiler_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/libxml2_2.9.9-1_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/libdb47_4.7.25.4.NC-5_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-db_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-decimal_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-unittest_2.7.16-2_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/base/terminfo_6.1-1_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/base/libncurses_6.1-1_i386_pentium4.ipk", "http://downloads.openwrt.org/releases/18.06.4/packages/i386_pentium4/packages/python-ncurses_2.7.16-2_i386_pentium4.ipk"]
	if "iso" in hostdata:
		print("ERROR: can not use iso install for openwrt")
		return
	elif "image" in hostdata:
		## generate network-configuration ##
		network = ""
		network += "\n"
		network += "config interface 'loopback'\n"
		network += "	option ifname 'lo'\n"
		network += "	option proto 'static'\n"
		network += "	option ipaddr '127.0.0.1'\n"
		network += "	option netmask '255.0.0.0'\n"
		network += "\n"
		network += "config globals 'globals'\n"
		network += "	option ula_prefix 'fd3c:ef70:e55d::/48'\n"
		network += "\n"
		for interface in hostdata["network"]["interfaces"]:
			if "ipv4" in hostdata["network"]["interfaces"][interface] and "link" in hostdata["network"]["interfaces"][interface]:
				for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
					network += "config interface '" + interface + "'\n"
					network += "	option type 'bridge'\n"
					network += "	option ifname '" + hostdata["network"]["interfaces"][interface]["link"] + "'\n"
					network += "	option proto 'static'\n"
					network += "	option ipaddr '" + ipv4["address"] + "'\n"
					network += "	option netmask '" + ipv4["netmask"] + "'\n"
					network += "	option gateway '" + hostdata["network"]["gateway"] + "'\n"
					network += "	option ip6assign '60'\n"
					network += "\n"
		network += "\n"
		with open(tempdir + "/network", "w") as ofile:
			ofile.write(network)
		dns = ""
		for nameserver in hostdata["network"]["nameservers"]:
			dns = nameserver
			break
		## generate dhcp/dns-configuration ##
		dhcp = ""
		dhcp += "\n"
		dhcp += "config dnsmasq\n"
		dhcp += "	option domainneeded '1'\n"
		dhcp += "	option localise_queries '1'\n"
		dhcp += "	option rebind_protection '1'\n"
		dhcp += "	option rebind_localhost '1'\n"
		dhcp += "	option local '/lan/'\n"
		dhcp += "	option domain 'lan'\n"
		dhcp += "	option expandhosts '1'\n"
		dhcp += "	option authoritative '1'\n"
		dhcp += "	option readethers '1'\n"
		dhcp += "	option leasefile '/tmp/dhcp.leases'\n"
		dhcp += "	option resolvfile '/tmp/resolv.conf.auto'\n"
		dhcp += "	option nonwildcard '1'\n"
		dhcp += "	option localservice '1'\n"
		dhcp += "	list server '" + dns + "'\n"
		dhcp += "\n"
		dhcp += "config dhcp 'lan'\n"
		dhcp += "	option interface 'lan'\n"
		dhcp += "	option start '100'\n"
		dhcp += "	option limit '150'\n"
		dhcp += "	option leasetime '12h'\n"
		dhcp += "	option dhcpv6 'server'\n"
		dhcp += "	option ra 'server'\n"
		dhcp += "\n"
		dhcp += "config dhcp 'wan'\n"
		dhcp += "	option interface 'wan'\n"
		dhcp += "	option ignore '1'\n"
		dhcp += "\n"
		dhcp += "config odhcpd 'odhcpd'\n"
		dhcp += "	option maindhcp '0'\n"
		dhcp += "	option leasefile '/tmp/hosts/odhcpd'\n"
		dhcp += "	option leasetrigger '/usr/sbin/odhcpd-update'\n"
		dhcp += "	option loglevel '4'\n"
		dhcp += "\n"
		with open(tempdir + "/dhcp", "w") as ofile:
			ofile.write(dhcp)
		## generate authorized_keys ##
		authorized_keys = ""
		for user in hostdata["users"]:
			if user == "root":
				if "sshpubkey" in hostdata["users"][user]:
					authorized_keys += hostdata["users"][user]["sshpubkey"] + "\n"
		with open(tempdir + "/authorized_keys", "w") as ofile:
			ofile.write(authorized_keys)

		## getting packages ##
		print("  getting packages")
		if not os.path.exists("openwrt/"):
			os.mkdir("openwrt")
		if not os.path.exists("openwrt/pkgs/"):
			os.mkdir("openwrt/pkgs")
		if not os.path.exists(tempdir + "/pkginst/"):
			os.mkdir(tempdir + "/pkginst")
		for pkg in packages:
			pkgname = pkg.split("/")[-1]
			if not os.path.exists("openwrt/pkgs/" + pkgname):
				print("   wget " + pkgname)
				os.system("wget -q -O 'openwrt/pkgs/" + pkgname + "' '" + pkg + "'")

		## mount image-partitions and copy config-files ##
		for disk in hostdata["disks"]:
			imgname = hostdata["image"].split("/")[-1]
			diskimage = "libvirt/images/" + hostdata["hostname"] + "_" + disk + "_" + imgname
			fdisk = os.popen("fdisk -lu '" + diskimage + "'").read()
			for line in fdisk.split("\n"):
				if line.startswith(diskimage):
					if line.split()[1] == "*":
						start = str(int(line.split()[2]) * 512)
					else:
						start = str(int(line.split()[1]) * 512)
					if os.path.exists(tempdir + "/img"):
						os.system("umount " + tempdir + "/img 2>/dev/null")
					else:
						os.mkdir(tempdir + "/img")
					print("  mount -o loop,offset=" + start + " '" + diskimage + "' '" + tempdir + "/img'")
					os.system("mount -o loop,offset=" + start + " '" + diskimage + "' '" + tempdir + "/img'")
					if os.path.exists(tempdir + "/img/etc/"):
						print("  cp '" + tempdir + "/network' '" + tempdir + "/img/etc/config/network'")
						os.system("cp '" + tempdir + "/network' '" + tempdir + "/img/etc/config/network'")
						print("  cp '" + tempdir + "/dhcp' '" + tempdir + "/img/etc/config/dhcp'")
						os.system("cp '" + tempdir + "/dhcp' '" + tempdir + "/img/etc/config/dhcp'")
						print("  cp '" + tempdir + "/authorized_keys' '" + tempdir + "/img/etc/dropbear/authorized_keys'")
						os.system("cp '" + tempdir + "/authorized_keys' '" + tempdir + "/img/etc/dropbear/authorized_keys'")
						print("  extract packages")
						for pkg in packages:
							pkgname = pkg.split("/")[-1]
							os.system("rm -rf '" + tempdir + "/pkginst/'*")
							os.system("tar -C '" + tempdir + "/pkginst/' -xzpf 'openwrt/pkgs/" + pkgname + "'")
							os.system("tar -C '" + tempdir + "/img/' -xzpf '" + tempdir + "/pkginst/data.tar.gz'")
							os.system("rm -f '" + tempdir + "/pkginst/debian-binary'")
							os.system("rm -f '" + tempdir + "/pkginst/control.tar.gz'")
							os.system("rm -f '" + tempdir + "/pkginst/data.tar.gz'")
					os.system("umount '" + tempdir + "/img'")

			break

		
