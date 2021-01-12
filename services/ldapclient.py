#!/usr/bin/python3
#
#q

import os
import json
import setuptools


def setup(hostdata, tempdir):
    for service, config in hostdata["services"].items():
        if service == "ldapclient":
            if (hostdata["os"] == "debian"):

                setup_ = ""


                setup = "#!/bin/bash\n"
                setup += setuptools.packages("vim less rsyslog ldap-utils libnss-ldap libpam-ldap nslcd sudo-ldap")

                setup += f"""
sed -i "s|^passwd:.*|passwd:         files ldap systemd|g" /etc/nsswitch.conf
sed -i "s|^group:.*|group:          files ldap systemd|g" /etc/nsswitch.conf
echo "sudoers:          files ldap" >> /etc/nsswitch.conf
"""

                ldap_conf = f"""
BASE {config["basedn"]}
URI {config["uri"]}

SUDOERS_BASE ou=SUDOers,{config["basedn"]}
SUDOERS_DEBUG 0

ldap_version 3
ssl start_tls
#tls_cacert /etc/ssl/cacert.pem
TLS_REQCERT allow

"""

                ldap_conf2 = f"""
BASE {config["basedn"]}
URI {config["uri"]}

pam_check_host_attr yes

ldap_version 3
ssl start_tls
#tls_cacert /etc/ssl/cacert.pem
TLS_REQCERT allow

"""

                setup += "mkdir -p /etc/ldap\n"
                setup += setuptools.file("/etc/ldap/ldap.conf", ldap_conf)
                setup += setuptools.file("/etc/libnss-ldap.conf", ldap_conf2)
                setup += setuptools.file("/etc/pam_ldap.conf", ldap_conf2)

                # create home on first login
                setup += "echo \"session     required      pam_mkhomedir.so skel=/etc/skel umask=0022\" >> /etc/pam.d/common-session\n"
                setup += "sed -i \"s|use_authtok ||g\" /etc/pam.d/common-password\n"

                # ssh-lpk (get key from ldap)
                sshlpksh = """#!/bin/bash
ldapsearch -x '(&(objectClass=posixAccount)(uid='"\$1"'))' 'sshPublicKey' | sed -n '/^ /{H;d};/sshPublicKey:/x;\$g;s/\\n *//g;s/sshPublicKey: //gp'
"""
                setup += setuptools.file("/usr/local/sbin/ssh-lpk.sh", sshlpksh, "755")

                setup += """
sed -i "s|#AuthorizedKeysCommand .*|AuthorizedKeysCommand /usr/local/sbin/ssh-lpk.sh|g" /etc/ssh/sshd_config
sed -i "s|#AuthorizedKeysCommandUser .*|AuthorizedKeysCommandUser nobody|g" /etc/ssh/sshd_config
"""


                setup += setuptools.autostart("rsyslog", "/etc/init.d/rsyslog start", "10")

                with open(tempdir + "/ldapclient.sh", "w") as ofile:
                    ofile.write(setup)
                return tempdir + "/ldapclient.sh"


    return ""


