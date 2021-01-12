
def autostart(name, command, pos="50"):
    script = "#############################################\n"
    script += "## add autostart for {name}\n"
    script += "#############################################\n"
    script += "mkdir -p /inits/\n"
    script += f"echo \"{command}\" > /inits/{pos}_{name}\n"
    script += "\n"
    script += "\n"
    return script

def packages(packages):
    script = "#############################################\n"
    script += "## install packages\n"
    script += "#############################################\n"
    script += "export DEBIAN_FRONTEND=noninteractive\n"
    script += "LANG=\"C\"\n"
    script += "apt-get update\n"
    script += "apt-get -y dist-upgrade\n"
    script += f"apt-get -y install {packages}\n"
    script += "\n"
    return script

def file(filename, data, chmod=None, chown=None):
    script = "#############################################\n"
    script += "## write file {filename}\n"
    script += "#############################################\n"
    script += f"cat <<EOF > \"{filename}\"\n"
    script += data
    script += "\nEOF\n"
    script += "\n"
    if chmod:
        script += f"chmod {chmod} \"{filename}\"\n"
        script += "\n"
    if chown:
        script += f"chmod {chown} \"{filename}\"\n"
        script += "\n"
    return script

def certificate(name):
    script = "#############################################\n"
    script += "## generate the SSL-Certificate for {name}\n"
    script += "#############################################\n"
    script += f"""
if ! test -e /etc/ssl/cacert.pem
then
	(
	mkdir -p /etc/ssl
	cd /etc/ssl
	cat <<EOF > ca.cfg 
cn = $DOMAINNAME
ca
cert_signing_key
EOF
	certtool --generate-privkey > cakey.pem
	certtool --generate-self-signed --load-privkey cakey.pem --template ca.cfg --outfile cacert.pem
    )
fi
(
mkdir -p /etc/ssl
cd /etc/ssl
cat <<EOF > slapd.cfg 
organization = $DOMAINNAME
cn = `hostname -f`
tls_www_server
encryption_key
signing_key
EOF
certtool --generate-privkey > {name}_key.pem
certtool --generate-certificate --load-privkey {name}_key.pem --load-ca-certificate cacert.pem --load-ca-privkey cakey.pem --template slapd.cfg --outfile {name}_cert.pem
)
cat /etc/ssl/{name}_cert.pem /etc/ssl/{name}_key.pem > /etc/ssl/{name}.pem

"""
    script += "\n"
    return script


