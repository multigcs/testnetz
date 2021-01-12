#!/usr/bin/python3
#
#

import os
import json
import setuptools


def setup(hostdata, tempdir):
    for service, config in hostdata["services"].items():
        if service == "haproxy":
            if (hostdata["os"] == "ubuntu" or hostdata["os"] == "debian"):


                haproxy_cfg = f"""
global
  log           /dev/log local6
  pidfile       /var/run/haproxy.pid
  chroot        /var/lib/haproxy
  maxconn       8192
  user          haproxy
  group         haproxy
  daemon
  stats socket /var/lib/haproxy/stats.socket mode 660 level admin
  ca-base /etc/ssl
  crt-base /etc/ssl

"""

                for port, proxy in config["ports"].items():
                    if proxy["type"] == "ssl":
                        bind = f"0.0.0.0:{port} ssl crt /etc/ssl/proxy.pem"
                    else:
                        bind = f"0.0.0.0:{port}"

                    nodes = ""
                    num = 1
                    for node in proxy["nodes"]:
                        if proxy["type"] == "ssl":
                            nodes += f"  server                snode-{num} {node}:{port} check fall 1 rise 1 inter 2s verify none check check-ssl\n"
                        else:
                            nodes += f"  server                node-{num} {node}:{port} check fall 1 rise 1 inter 2s\n"
                        num += 1

                    haproxy_cfg += f"""
# PORT: {port} ({proxy["type"]})
frontend service_front_{port}
  mode                  tcp
  log                   global
  bind                  {bind}
  description           Service {port} ({proxy["type"]})
  option                tcplog
  option                logasap
  option                socket-stats
  option                tcpka
  timeout client        5s
  default_backend       service_back_{port}

backend service_back_{port}
{nodes}
  mode                  tcp
  balance               leastconn
  timeout server        2s
  timeout connect       1s
  option                tcpka
  option                tcp-check
  tcp-check             connect port {port}
  tcp-check             send-binary 300c0201            # LDAP bind request "<ROOT>" simple
  tcp-check             send-binary 01                  # message ID
  tcp-check             send-binary 6007                # protocol Op
  tcp-check             send-binary 0201                # bind request
  tcp-check             send-binary 03                  # LDAP v3
  tcp-check             send-binary 04008000            # name, simple authentication
  tcp-check             expect binary 0a0100            # bind response + result code: success
  tcp-check             send-binary 30050201034200      # unbind request

"""

                setup = "#!/bin/bash\n"
                setup += setuptools.packages("net-tools vim less gnutls-bin wget rsyslog haproxy")
                setup += setuptools.certificate("proxy")
                setup += setuptools.file("/etc/haproxy/haproxy.cfg", haproxy_cfg)
                setup += setuptools.autostart("rsyslog", "/etc/init.d/rsyslog start", "10")
                setup += setuptools.autostart("haproxy", "/etc/init.d/haproxy start", "70")

                with open(tempdir + "/haproxy.sh", "w") as ofile:
                    ofile.write(setup)
                return tempdir + "/haproxy.sh"
    return ""


