#!/usr/bin/python3
#
#

import os
import json


def setup(hostdata, tempdir):
	setup = ""
	for service in hostdata["services"]:
		if service == "checkmkagent":
			if hostdata["os"] in ["ubuntu", "debian", "centos", "fedora", "opensuse", "openbsd", "freebsd"]:
				setup += "#!/bin/sh\n"
				setup += "\n"
				setup += "cd /tmp\n"
				setup += "hostid=\"" + hostdata["hostid"] + "\"\n"
				setup += "bootserver=\"" + hostdata["bootserver"] + "\"\n"
				setup += "cmkserver=\"" + hostdata["services"]["checkmkagent"]["server"] + "\"\n"
				setup += "\n"
				if hostdata["os"] == "ubuntu" or hostdata["os"] == "debian":
					os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
					os.system("cp -a files/ubuntu/check-mk-agent_1.6.0p7-1_all.deb /var/www/html/hosts/" + hostdata["hostid"] + "/")
					setup += "apt-get install -y xinetd wget\n"
					setup += "filename=\"check-mk-agent_1.6.0p7-1_all.deb\"\n"
					setup += "wget -O $filename http://$bootserver/hosts/$hostid/$filename\n"
					setup += "dpkg -i $filename\n"
					setup += "apt-get install -f -y\n"
					setup += "\n"
				elif hostdata["os"] == "centos" or hostdata["os"] == "fedora":
					os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
					os.system("cp -a files/centos/check-mk-agent-1.6.0p7-1.noarch.rpm /var/www/html/hosts/" + hostdata["hostid"] + "/")
					setup += "yum install -y xinetd wget\n"
					setup += "filename=\"check-mk-agent-1.6.0p7-1.noarch.rpm\"\n"
					setup += "wget -O $filename http://$bootserver/hosts/$hostid/$filename\n"
					setup += "rpm -vi $filename\n"
					setup += "service firewalld restart\n"
					setup += "firewall-cmd --permanent --zone=public --add-port=6556/tcp || true\n"
					setup += "firewall-cmd --reload || true\n"
					setup += "\n"
				elif hostdata["os"] == "opensuse":
					os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
					os.system("cp -a files/opensuse/check-mk-agent-1.6.0p7-1.noarch.rpm /var/www/html/hosts/" + hostdata["hostid"] + "/")
					setup += "zypper install -y xinetd wget\n"
					setup += "filename=\"check-mk-agent-1.6.0p7-1.noarch.rpm\"\n"
					setup += "wget -O $filename http://$bootserver/hosts/$hostid/$filename\n"
					setup += "rpm -vi $filename\n"
					setup += "service firewalld restart\n"
					setup += "firewall-cmd --permanent --zone=public --add-port=6556/tcp || true\n"
					setup += "firewall-cmd --reload || true\n"
					setup += "\n"
				elif hostdata["os"] == "openbsd":
					os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
					os.system("cp -a files/openbsd/check_mk_agent.openbsd /var/www/html/hosts/" + hostdata["hostid"] + "/")
					setup += "pkg_add wget\n"
					setup += "filename=\"check_mk_agent.openbsd\"\n"
					setup += "wget -O $filename http://$bootserver/hosts/$hostid/$filename\n"
					setup += "cp $filename /usr/bin/check_mk_agent\n"
					setup += "chmod 755 /usr/bin/check_mk_agent\n"
					setup += "\n"
				elif hostdata["os"] == "freebsd":
					os.system("mkdir -p /var/www/html/hosts/" + hostdata["hostid"])
					os.system("cp -a files/freebsd/check_mk_agent.freebsd /var/www/html/hosts/" + hostdata["hostid"] + "/")
					setup += "pkg install -y bash wget\n"
					setup += "filename=\"check_mk_agent.freebsd\"\n"
					setup += "wget -O $filename http://$bootserver/hosts/$hostid/$filename\n"
					setup += "cp $filename /usr/bin/check_mk_agent\n"
					setup += "chmod 755 /usr/bin/check_mk_agent\n"
					setup += "\n"

				if hostdata["os"] == "openbsd":
					setup += "echo \"check_mk    stream   tcp   nowait   root   /usr/bin/check_mk_agent.openbsd\" >> /etc/inetd.conf\n"
					setup += "echo \"check_mk  6556/tcp\" >> /etc/services\n"
					setup += "echo \"\" >> /etc/rc.conf.local\n"
					setup += "echo \"inetd_flags=\" >> /etc/rc.conf.local\n"
					setup += "echo \"inetd=YES\" >> /etc/rc.conf.local\n"
					setup += "inetd &\n"
					setup += "\n"
				elif hostdata["os"] == "freebsd":
					setup += "echo \"check_mk    stream   tcp   nowait   root   /usr/bin/check_mk_agent.freebsd\" >> /etc/inetd.conf\n"
					setup += "echo \"check_mk  6556/tcp\" >> /etc/services\n"
					setup += "echo \"\"  >> /etc/rc.conf\n"
					setup += "echo \"inetd_enable=yes\"  >> /etc/rc.conf\n"
					setup += "echo \"inetd_flags=-wW\" >> /etc/rc.conf\n"
					setup += "echo \"\"  >> /etc/rc.conf\n"
					setup += "echo \"\"  >> /etc/hosts.allow\n"
					setup += "echo \"# Allow nagios server to access us\"  >> /etc/hosts.allow\n"
					setup += "echo \"check_mk_agent : 127.0.0.1 : allow\"  >> /etc/hosts.allow\n"
					setup += "echo \"check_mk_agent : $cmkserver : allow\"  >> /etc/hosts.allow\n"
					setup += "echo \"check_mk_agent : ALL : deny\"  >> /etc/hosts.allow\n"
					setup += "echo \"\"  >> /etc/hosts.allow\n"
					setup += "/etc/rc.d/inetd start\n"
					setup += "\n"
				else:
					setup += "cat <<EOF > /etc/xinetd.d/check_mk\n"
					setup += "service check_mk\n"
					setup += "{\n"
					setup += "	type           = UNLISTED\n"
					setup += "	port           = 6556\n"
					setup += "	socket_type    = stream\n"
					setup += "	protocol       = tcp\n"
					setup += "	wait           = no\n"
					setup += "	user           = root\n"
					setup += "	server         = /usr/bin/check_mk_agent\n"
					setup += "	#only_from      = 127.0.0.1 $cmkserver\n"
					setup += "	log_on_success =\n"
					setup += "	disable        = no\n"
					setup += "}\n"
					setup += "EOF\n"
					setup += "\n"
					setup += "if ! test -e /.dockerenv\n"
					setup += "then\n"
					setup += " #service xinetd stop || true\n"
					setup += " #service xinetd start || true\n"
					setup += " systemctl stop xinetd || true\n"
					setup += " systemctl start xinetd || true\n"
					setup += "fi\n"
					setup += "\n"
				with open(tempdir + "/checkmkagent.sh", "w") as ofile:
					ofile.write(setup)
				return tempdir + "/checkmkagent.sh"
	return ""


