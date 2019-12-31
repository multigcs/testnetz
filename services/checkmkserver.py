#!/usr/bin/python3
#
#

import os
import json


def setup(hostdata, tempdir):
	setup = ""
	for service in hostdata["services"]:
		if service == "checkmkserver":
			if (hostdata["os"] == "ubuntu"):
				setup += "#!/bin/sh\n"
				setup += "cd /tmp\n"
				setup += "site=\"" + hostdata["services"]["checkmkserver"]["site"] + "\"\n"
				setup += "password=\"" + hostdata["services"]["checkmkserver"]["password"] + "\"\n"
				setup += "\n"
				setup += "apt-get install -y curl traceroute dialog graphviz apache2 apache2-utils libdbi1 libevent-1.4-2 libltdl7 libpango1.0-0 libreadline5\n"
				setup += "test -e check-mk-raw-1.6.0p7_0.bionic_amd64.deb || curl -L -O https://checkmk.de/support/1.6.0p7/check-mk-raw-1.6.0p7_0.bionic_amd64.deb\n"
				setup += "dpkg -i check-mk-raw-1.6.0p7_0.bionic_amd64.deb\n"
				setup += "apt-get install -y -f\n"
				setup += "\n"
				setup += "omd create --admin-password=\"$password\" $site\n"
				setup += "omd config $site set LIVESTATUS_TCP on\n"
				setup += "omd config $site set LIVESTATUS_TCP_TLS off\n"
				setup += "\n"
				setup += "systemctl enable check-mk-raw-1.6.0p7\n"
				setup += "service check-mk-raw-1.6.0p7 stop\n"
				setup += "service check-mk-raw-1.6.0p7 start\n"
				setup += "\n"
				setup += "omd restart\n"
				setup += "\n"
				setup += "service apache2 stop\n"
				setup += "service apache2 start\n"
				setup += "\n"
				setup += "echo \"<a href='/$site/'>CheckMK</a><br />\" >> /var/www/html/links.html\n"
				setup += "ln -sf /var/www/html/links.html /var/www/html/index.html\n"
				setup += "\n"
				with open(tempdir + "/checkmkserver.sh", "w") as ofile:
					ofile.write(setup)
				return tempdir + "/checkmkserver.sh"
	return ""


