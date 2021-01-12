#!/usr/bin/python3
#
#

import os
import json
import setuptools

def setup(hostdata, tempdir):
    for service in hostdata["services"]:
        if service == "keepalived":
            if (hostdata["os"] == "debian"):

                keepalived_conf = f"""
vrrp_instance VI_1 {{
        state {hostdata["services"]["keepalived"]["role"]}
        interface eth0
        virtual_router_id {hostdata["services"]["keepalived"]["vrid"]}
        priority {hostdata["services"]["keepalived"]["priority"]}
        advert_int 1
        authentication {{
              auth_type PASS
              auth_pass 12345
        }}
        virtual_ipaddress {{
              {hostdata["services"]["keepalived"]["address"]}
        }}
}}
                """

                setup = "#!/bin/bash\n"
                setup += setuptools.packages("net-tools vim less gnutls-bin wget rsyslog keepalived")
                setup += setuptools.file("/etc/keepalived/keepalived.conf", keepalived_conf)
                setup += setuptools.autostart("rsyslog", "/etc/init.d/rsyslog start", "10")
                setup += setuptools.autostart("keepalived", "/etc/init.d/keepalived start", "90")

                with open(tempdir + "/keepalived.sh", "w") as ofile:
                    ofile.write(setup)
                return tempdir + "/keepalived.sh"
    return ""


