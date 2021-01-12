#!/usr/bin/python3
#
#

import os
import json
import setuptools


def setup(hostdata, tempdir):
    for service, config in hostdata["services"].items():
        if service == "ldapadmin":
            if (hostdata["os"] == "debian"):

                setup = "#!/bin/bash\n"
                setup += setuptools.packages("net-tools vim less gnutls-bin ldap-utils wget git rsyslog apache2 libapache2-mod-php php-ldap php-xml")
                setup += setuptools.certificate("apache2")
                removeTemplates = [
                    'courierMailAlias',
                    'courierMailAccount',
                    'sambaSAMAccount',
                    'sambaGroupMapping',
                ]
                for template in removeTemplates:
                    setup += f"rm -rf /var/www/html/phpldapadmin/templates/creation/{template}.xml\n"

                setup += f"""

cd /var/www/html
git clone https://github.com/breisig/phpLDAPadmin.git
mv phpLDAPadmin phpldapadmin


cat <<EOF > phpldapadmin/config/config.php
<?php

\$config->custom->appearance['friendly_attrs'] = array(
	'facsimileTelephoneNumber' => 'Fax',
	'gid'                      => 'Group',
	'mail'                     => 'Email',
	'telephoneNumber'          => 'Telephone',
	'uid'                      => 'User Name',
	'userPassword'             => 'Password'
);

\$servers = new Datastore();
\$servers->newServer('ldap_pla');
\$servers->setValue('server', 'name', 'My LDAP Server');
\$servers->setValue('server', 'host', '{config["server"]}');
\$servers->setValue('server', 'base', array('{config["basedn"]}'));
\$servers->setValue('server', 'tls', false);
\$servers->setValue('login', 'anon_bind', false);

?>
EOF

"""


                ldap_conf = f"""
BASE {config["basedn"]}
URI {config["uri"]}

ldap_version 3
ssl start_tls
#tls_cacert /etc/ssl/cacert.pem
TLS_REQCERT allow

"""
                setup += "mkdir -p /etc/ldap\n"
                setup += setuptools.file("/etc/ldap/ldap.conf", ldap_conf)
                setup += setuptools.autostart("rsyslog", "/etc/init.d/rsyslog start", "10")
                setup += setuptools.autostart("apache2", "/etc/init.d/apache2 start", "60")

                with open(tempdir + "/ldapadmin.sh", "w") as ofile:
                    ofile.write(setup)
                return tempdir + "/ldapadmin.sh"
    return ""


