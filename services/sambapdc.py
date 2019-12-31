#!/usr/bin/python3
#
# https://www.unixmen.com/setting-samba-primary-domain-controller-centos-7/
#

import os
import json


def setup(hostdata, tempdir):
	setup = ""
	for service in hostdata["services"]:
		if service == "sambapdc":
			if hostdata["os"] == "ubuntu" or hostdata["os"] == "centos":
				setup += "#!/bin/sh\n"
				setup += "\n"
				setup += "realm=\"" + hostdata["domainname"].upper() + "\"\n"
				setup += "hostname=\"" + hostdata["hostname"] + "\"\n"
				setup += "adserver=\"127.0.0.1\"\n"
				setup += "sambadomain=\"" + hostdata["services"]["sambapdc"]["sambadomain"] + "\"\n"
				setup += "adminpasswd=\"" + hostdata["services"]["sambapdc"]["adminpasswd"] + "\"\n"
				setup += "\n"
				if (hostdata["os"] == "ubuntu"):
					setup += "DEBIAN_FRONTEND=noninteractive apt-get install -y samba winbind krb5-user ldb-tools\n"
					setup += "\n"
				if (hostdata["os"] == "centos"):
					setup += "yum install -y samba samba-client samba-dc-libs samba-krb5-printing samba-pidl samba-test samba-test-libs samba-winbind samba-winbind-clients samba-winbind-krb5-locator samba-winbind-modules\n"
					setup += "\n"
				setup += "cat <<EOF > /etc/samba/smb.conf\n"
				setup += "\n"
				setup += "[Global]\n"
				setup += "  workgroup = $sambadomain\n"
				setup += "  security = user\n"
				setup += "  domain master = yes\n"
				setup += "  domain logons = yes\n"
				setup += "  local master = yes\n"
				setup += "  preferred master = yes\n"
				setup += "  passdb backend = tdbsam\n"
				setup += "  logon path = \\%L\Profiles\%U\n"
				setup += "  logon script = logon.bat\n"
				setup += "  add machine script = /usr/sbin/useradd -d /dev/null -g 200 -s /sbin/nologin -M %u\n"
				setup += "\n"
				setup += "[homes]\n"
				setup += "  comment = Home Directories\n"
				setup += "  browseable = yes\n"
				setup += "  writable = yes\n"
				setup += "\n"
				setup += "[printers]\n"
				setup += "  comment = All Printers\n"
				setup += "  path = /var/spool/samba\n"
				setup += "  printable = Yes\n"
				setup += "  print ok = Yes\n"
				setup += "  browseable = No\n"
				setup += "\n"
				setup += "[netlogon]\n"
				setup += "  comment = Network Logon Service\n"
				setup += "  path = /var/lib/samba/netlogon\n"
				setup += "  browseable = No\n"
				setup += "  writable = No\n"
				setup += "\n"
				setup += "[Profiles]\n"
				setup += "  path = /var/lib/samba/profiles\n"
				setup += "  create mask = 0755\n"
				setup += "  directory mask = 0755\n"
				setup += "  writable = Yes\n"
				setup += "\n"
				setup += "EOF\n"
				setup += "\n"
				setup += "mkdir -m 1777 /var/lib/samba/netlogon\n"
				setup += "mkdir -m 1777 /var/lib/samba/profiles\n"
				setup += "groupadd -g 200 machine\n"
				setup += "smbpasswd -m -a $hostname$\n"
				setup += "\n"
				setup += "echo -e \"$adminpasswd\\n$adminpasswd\" | smbpasswd -a root\n"
				setup += "\n"

				if (hostdata["os"] == "ubuntu"):
					setup += "service smbd stop\n"
					setup += "service smbd start\n"
					setup += "service nmbd stop\n"
					setup += "service nmbd start\n"
					setup += "service samba-ad-dc stop\n"
					setup += "service samba-ad-dc start\n"
					setup += "\n"
				if (hostdata["os"] == "centos"):
					setup += "systemctl enable smb\n"
					setup += "systemctl enable nmb\n"
					setup += "service smb stop\n"
					setup += "service smb start\n"
					setup += "service nmb stop\n"
					setup += "service nmb start\n"
					setup += "\n"
					setup += "service firewalld restart\n"
					setup += "firewall-cmd --permanent --add-port=53/tcp\n"
					setup += "firewall-cmd --permanent --add-port=53/udp\n"
					setup += "firewall-cmd --permanent --add-port=88/tcp\n"
					setup += "firewall-cmd --permanent --add-port=88/udp\n"
					setup += "firewall-cmd --permanent --add-port=135/tcp\n"
					setup += "firewall-cmd --permanent --add-port=137/tcp\n"
					setup += "firewall-cmd --permanent --add-port=137/udp\n"
					setup += "firewall-cmd --permanent --add-port=138/udp\n"
					setup += "firewall-cmd --permanent --add-port=139/tcp\n"
					setup += "firewall-cmd --permanent --add-port=389/tcp\n"
					setup += "firewall-cmd --permanent --add-port=389/udp\n"
					setup += "firewall-cmd --permanent --add-port=445/tcp\n"
					setup += "firewall-cmd --permanent --add-port=464/tcp\n"
					setup += "firewall-cmd --permanent --add-port=464/udp\n"
					setup += "firewall-cmd --permanent --add-port=636/tcp\n"
					setup += "firewall-cmd --permanent --add-port=1024-5000/tcp\n"
					setup += "firewall-cmd --permanent --add-port=1024-5000/udp\n"
					setup += "firewall-cmd --permanent --add-port=3268/tcp\n"
					setup += "firewall-cmd --permanent --add-port=3269/tcp\n"
					setup += "firewall-cmd --permanent --add-port=5353/tcp\n"
					setup += "firewall-cmd --permanent --add-port=5353/udp\n"
					setup += "\n"
					setup += "firewall-cmd --reload\n"
					setup += "\n"
					setup += "setsebool -P samba_domain_controller on\n"
					setup += "setsebool -P samba_enable_home_dirs on\n"
					setup += "chcon -t samba_share_t /var/lib/samba/netlogon\n"
					setup += "chcon -t samba_share_t /var/lib/samba/profiles\n"
					setup += "\n"

				with open(tempdir + "/sambapdc.sh", "w") as ofile:
					ofile.write(setup)
				return tempdir + "/sambapdc.sh"
	return ""

