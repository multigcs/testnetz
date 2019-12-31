#!/usr/bin/python3
#
# https://www.elastic.co/guide/en/beats/metricbeat/current/metricbeat-starting.html
#

import os
import json


def setup(hostdata, tempdir):
	setup = ""
	for service in hostdata["services"]:
		if service == "visansible":
			if (hostdata["os"] == "ubuntu" or hostdata["os"] == "centos" or hostdata["os"] == "opensuse"):
				setup += "#!/bin/sh\n"
				setup += "cd /tmp\n"
				if hostdata["os"] == "ubuntu":
					setup += "apt-get install -y git\n"
					setup += "\n"
				elif hostdata["os"] == "centos" or hostdata["os"] == "opensuse":
					setup += "yum install -y git\n"
					setup += "\n"
				setup += "cd /opt\n"
				setup += "git clone http://github.com/multigcs/visansible\n"
				setup += "\n"
				setup += "(cd /opt/visansible/ ; nohup python3 visansible.py >> /var/log/visansible.log 2>&1 &)\n"
				setup += "\n"

				if hostdata["os"] == "ubuntu":
					setup += "apt-get install -y apache2\n"
					setup += "\n"
					setup += "cat <<EOF > /etc/apache2/conf-available/visansible.conf\n"
					setup += "ProxyPreserveHost on\n"
					setup += "<Location /visansible>\n"
					setup += "    ProxyPass http://localhost:8081\n"
					setup += "    ProxyPassReverse http://localhost:8081\n"
					setup += "</Location>\n"
					setup += "\n"
					setup += "EOF\n"
					setup += "\n"
					setup += "a2enmod proxy\n"
					setup += "a2enmod proxy_http\n"
					setup += "a2enconf visansible\n"
					setup += "\n"
					setup += "service apache2 stop\n"
					setup += "service apache2 start\n"
					setup += "\n"
				elif hostdata["os"] == "centos":
					setup += "yum install -y httpd\n"
					setup += "\n"
					setup += "cat <<EOF > /etc/httpd/conf.d/visansible.conf\n"
					setup += "ProxyPreserveHost on\n"
					setup += "<Location /visansible>\n"
					setup += "    ProxyPass http://localhost:8081\n"
					setup += "    ProxyPassReverse http://localhost:8081\n"
					setup += "</Location>\n"
					setup += "\n"
					setup += "EOF\n"
					setup += "\n"
					setup += "setsebool -P httpd_can_network_connect on\n"
					setup += "\n"
					setup += "service httpd stop\n"
					setup += "service httpd start\n"
					setup += "\n"
					setup += "firewall-cmd --permanent --zone=public --add-port=80/tcp\n"
					setup += "firewall-cmd --permanent --zone=public --add-port=5044/tcp\n"
					setup += "firewall-cmd --reload\n"
					setup += "\n"
				setup += "echo \"<a href='/visansible/'>Visansible</a><br />\" >> /var/www/html/links.html\n"
				setup += "ln -sf /var/www/html/links.html /var/www/html/index.html\n"

				with open(tempdir + "/visansible.sh", "w") as ofile:
					ofile.write(setup)
				return tempdir + "/visansible.sh"
	return ""


