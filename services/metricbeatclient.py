#!/usr/bin/python3
#
# https://www.elastic.co/guide/en/beats/metricbeat/current/metricbeat-starting.html
#

import os
import json


def setup(hostdata, tempdir):
	setup = ""
	for service in hostdata["services"]:
		if service == "metricbeatclient":
			if (hostdata["os"] == "ubuntu" or hostdata["os"] == "debian" or hostdata["os"] == "centos" or hostdata["os"] == "opensuse"):
				setup += "#!/bin/sh\n"
				setup += "cd /tmp\n"
				if hostdata["os"] == "ubuntu" or hostdata["os"] == "debian":
					setup += "apt-get install -y curl\n"
					setup += "test -e metricbeat-7.5.0-amd64.deb || curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-7.5.0-amd64.deb\n"
					setup += "dpkg -i metricbeat-7.5.0-amd64.deb\n"
					setup += "apt-get install -y -f\n"
					setup += "\n"
				elif hostdata["os"] == "centos" or hostdata["os"] == "opensuse":
					setup += "yum install -y curl\n"
					setup += "test -e metricbeat-7.5.0-x86_64.rpm || curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-7.5.0-x86_64.rpm\n"
					setup += "rpm -vi metricbeat-7.5.0-x86_64.rpm\n"
					setup += "\n"
				setup += "cat <<EOF > /etc/metricbeat/metricbeat.yml\n"
				setup += "\n"
				setup += "metricbeat.config.modules:\n"
				setup += "  path: \${path.config}/modules.d/*.yml\n"
				setup += "  reload.enabled: false\n"
				setup += "\n"
				setup += "setup.template.settings:\n"
				setup += "  index.number_of_shards: 1\n"
				setup += "  index.codec: best_compression\n"
				setup += "\n"
				setup += "setup.kibana:\n"
				setup += "  host: \"localhost:5601/kibana\"\n"
				setup += "\n"
				setup += "\n"
				if "output" in hostdata["services"]["metricbeatclient"]:
					if "type" in hostdata["services"]["metricbeatclient"]["output"] and "hosts" in hostdata["services"]["metricbeatclient"]["output"]:
						setup += "output." + hostdata["services"]["metricbeatclient"]["output"]["type"] + ":\n"
						setup += "  hosts: [\"" + "\", \"".join(hostdata["services"]["metricbeatclient"]["output"]["hosts"]) + "\"]\n"
						setup += "\n"

				setup += "processors:\n"
				setup += "  - add_host_metadata: ~\n"
				setup += "  - add_cloud_metadata: ~\n"
				setup += "  - add_docker_metadata: ~\n"
				setup += "  - add_kubernetes_metadata: ~\n"
				setup += "\n"
				setup += "EOF\n"
				setup += "\n"
				if "modules" in hostdata["services"]["metricbeatclient"]:
					for module in hostdata["services"]["metricbeatclient"]["modules"]:
						setup += "metricbeat modules enable " + module + "\n"
				setup += "\n"
				setup += "systemctl enable metricbeat\n"
				setup += "systemctl stop metricbeat\n"
				setup += "systemctl start metricbeat\n"
				setup += "\n"
				setup += "#metricbeat setup -e\n"
				setup += "\n"
				setup += "\n"
				with open(tempdir + "/metricbeat.sh", "w") as ofile:
					ofile.write(setup)
				return tempdir + "/metricbeat.sh"
	return ""


