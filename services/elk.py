#!/usr/bin/python3
#
# https://www.elastic.co/guide/en/elastic-stack-get-started/7.5/get-started-elastic-stack.html#install-logstash
#

import os
import json


def setup(hostdata, tempdir):
	setup = ""
	for service in hostdata["services"]:
		if service == "elk":
			if (hostdata["os"] == "ubuntu" or hostdata["os"] == "centos" or hostdata["os"] == "opensuse"):
				# elasticsearch
				setup += "#!/bin/sh\n"
				setup += "cd /tmp\n"
				if hostdata["os"] == "ubuntu":
					setup += "touch /etc/default/logstash\n"
					setup += "apt-get install -y curl openjdk-8-jdk\n"
					setup += "test -e elasticsearch-7.5.0-amd64.deb || curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.5.0-amd64.deb\n"
					setup += "dpkg -i elasticsearch-7.5.0-amd64.deb\n"
					setup += "apt-get install -y -f\n"
					setup += "\n"
				elif hostdata["os"] == "centos" or hostdata["os"] == "opensuse":
					setup += "yum install -y curl tar net-tools java-11-openjdk\n"
					setup += "test -e elasticsearch-7.5.0-x86_64.rpm || curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.5.0-x86_64.rpm\n"
					setup += "rpm -vi elasticsearch-7.5.0-x86_64.rpm\n"
					setup += "\n"
				setup += "service elasticsearch stop\n"
				setup += "service elasticsearch start\n"
				setup += "\n"

				# kibana
				setup += "cd /opt\n"
				setup += "test -e kibana-7.5.0-linux-x86_64.tar.gz || curl -L -O https://artifacts.elastic.co/downloads/kibana/kibana-7.5.0-linux-x86_64.tar.gz\n"
				setup += "tar xzvf kibana-7.5.0-linux-x86_64.tar.gz\n"
				setup += "cd kibana-7.5.0-linux-x86_64/\n"
				setup += "sed -i \"s|^#server.basePath.*|server.basePath: '/kibana'|g\" config/kibana.yml\n"
				setup += "sed -i \"s|^#server.rewriteBasePath.*|server.rewriteBasePath: true|g\" config/kibana.yml\n"
				setup += "(cd /opt/kibana-7.5.0-linux-x86_64/ ; nohup bin/kibana --allow-root >> /var/log/kibana.log 2>&1 &)\n"
				setup += "cd /tmp\n"
				setup += "\n"

				# logstash
				if hostdata["os"] == "ubuntu":
					setup += "test -e logstash-7.5.0.deb || curl -L -O https://artifacts.elastic.co/downloads/logstash/logstash-7.5.0.deb\n"
					setup += "dpkg -i logstash-7.5.0.deb\n"
					setup += "apt-get install -y -f\n"
					setup += "\n"
				elif hostdata["os"] == "centos" or hostdata["os"] == "opensuse":
					setup += "test -e logstash-7.5.0.rpm || curl -L -O https://artifacts.elastic.co/downloads/logstash/logstash-7.5.0.rpm\n"
					setup += "rpm -vi logstash-7.5.0.rpm\n"
					setup += "\n"
				setup += "cat <<EOF > /etc/logstash/conf.d/beats.conf\n"
				setup += "\n"
				setup += "input {\n"
				setup += "  beats {\n"
				setup += "    port => 5044\n"
				setup += "  }\n"
				setup += "}\n"
				setup += "\n"
				setup += "output {\n"
				setup += "  elasticsearch {\n"
				setup += "    hosts => \"localhost:9200\"\n"
				setup += "    manage_template => false\n"
				setup += "    index => \"%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}\"\n"
				setup += "  }\n"
				setup += "}\n"
				setup += "\n"
				setup += "EOF\n"
				setup += "\n"
				setup += "service logstash stop\n"
				setup += "service logstash start\n"
				setup += "(nohup /usr/share/logstash/bin/logstash --path.settings /etc/logstash/ -f /etc/logstash/conf.d/beats.conf >> /var/log/logstash.log 2>&1 &)\n"
				setup += "\n"

				# metricbeat
				if hostdata["os"] == "ubuntu":
					setup += "test -e metricbeat-7.5.0-amd64.deb || curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-7.5.0-amd64.deb\n"
					setup += "dpkg -i metricbeat-7.5.0-amd64.deb\n"
					setup += "apt-get install -y -f\n"
					setup += "\n"
				elif hostdata["os"] == "centos" or hostdata["os"] == "opensuse":
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
				setup += "output.elasticsearch:\n"
				setup += "  hosts: [\"localhost:9200\"]\n"
				setup += "\n"
				setup += "processors:\n"
				setup += "  - add_host_metadata: ~\n"
				setup += "  - add_cloud_metadata: ~\n"
				setup += "  - add_docker_metadata: ~\n"
				setup += "  - add_kubernetes_metadata: ~\n"
				setup += "\n"
				setup += "EOF\n"
				setup += "\n"
				setup += "systemctl enable metricbeat\n"
				setup += "service metricbeat stop\n"
				setup += "service metricbeat start\n"
				setup += "\n"
				setup += "metricbeat setup -e\n"
				setup += "\n"

				# apache reverse-proxy for kibana
				if hostdata["os"] == "ubuntu":
					setup += "apt-get install -y apache2\n"
					setup += "\n"
					setup += "cat <<EOF > /etc/apache2/conf-available/kibana.conf\n"
					setup += "ProxyPreserveHost on\n"
					setup += "<Location /kibana>\n"
					setup += "    ProxyPass http://localhost:5601/kibana\n"
					setup += "    ProxyPassReverse http://localhost:5601/kibana\n"
					setup += "</Location>\n"
					setup += "\n"
					setup += "EOF\n"
					setup += "\n"
					setup += "a2enmod proxy\n"
					setup += "a2enmod proxy_http\n"
					setup += "a2enconf kibana\n"
					setup += "\n"
					setup += "service apache2 stop\n"
					setup += "service apache2 start\n"
					setup += "\n"
				elif hostdata["os"] == "centos":
					setup += "yum install -y httpd\n"
					setup += "\n"
					setup += "cat <<EOF > /etc/httpd/conf.d/kibana.conf\n"
					setup += "ProxyPreserveHost on\n"
					setup += "<Location /kibana>\n"
					setup += "    ProxyPass http://localhost:5601/kibana\n"
					setup += "    ProxyPassReverse http://localhost:5601/kibana\n"
					setup += "</Location>\n"
					setup += "\n"
					setup += "EOF\n"
					setup += "\n"
					setup += "setsebool -P httpd_can_network_connect on\n"
					setup += "\n"
					setup += "service httpd stop\n"
					setup += "service httpd start\n"
					setup += "\n"
					setup += "service firewalld restart\n"
					setup += "firewall-cmd --permanent --zone=public --add-port=80/tcp\n"
					setup += "firewall-cmd --permanent --zone=public --add-port=5044/tcp\n"
					setup += "firewall-cmd --reload\n"
					setup += "\n"
				setup += "echo \"<a href='/kibana/'>Kibana</a><br />\" >> /var/www/html/links.html\n"
				setup += "ln -sf /var/www/html/links.html /var/www/html/index.html\n"
				setup += "\n"
				with open(tempdir + "/elk.sh", "w") as ofile:
					ofile.write(setup)
				return tempdir + "/elk.sh"
	return ""


