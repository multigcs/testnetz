# testnetz
easy autoinstaller for os tests using libvirt, docker and openvswitch

* it builds a virtual network using openvswitch

* runs virtaual machines inside kvm using libvirt

* and virtaual containers using docker

* all systems starts with unattended autoinstaller controled by .json files

* you can also install baremetal-systems using PXE


# !!! Warning !!!

### this scripts copy files and maybe overwrites files in:

* /var/www/html (./hosts ./install.conf ./openbsd-6.6 -- for post-install scripts and the openbsd-autoinstaller)

* /var/lib/tftpboot (./pxelinux.0 ./pxelinux.cfg/default and many more)

* /etc/dnsmasq.conf (overwrite by init-ovs.sh)


### and setup some network devices:

* openvswitch (by init-ovs.sh)

* iface virbr0 will be deactivate (by init-ovs.sh)

* /proc/sys/net/ipv4/ip_forward set to 1 (by init-ovs.sh)

* ovs-vsctl add-br ovsbr and set IP (by init-ovs.sh)

* ovs-vsctl add-br ovsbr2 and set IP (by init-ovs.sh)


# TODO's

* windows: missing fix-links to download WinPE iso and some tools

* freebsd: autoinstaller via PXE (at the moment, only ISO-Autoinstaller works)

* netbsd: autoinstaller (there are no official autoinstaller exist)

* osx: autoinstaller (no install will work)

* all OS's: add more predifined service installer



# Quickstart

### install virt-manager, libvirt, tftp-server, dhcp-server, dnsmasq and webserver

#### for PXE-Boot you need to setup your dhcp-server:

* example-file: doc/dhcpd.conf


### starting web-frontend (only for overview - http://127.0.0.1:8082)

 ./testnetz.py


### check and run ovs init-script:

 vi init-ovs.sh
 sh init-ovs.sh


### start ubuntu installation inside kvm using libvirt and Install-ISO (first start take a while, downloading the Ubuntu-ISO)

 ./init.py -f hosts/ubuntu1910-libvirt.json


### prepare pxe boot: (this take a while, downloading some boot-images and kernels for PXE / ~900MB)

 ./init.py -p


### start centos installation inside kvm using libvirt and PXE-Boot

 ./init.py -f hosts/centos8-pxe.json


### start debian installation inside docker

 ./init.py -f hosts/debian10-docker.json



# Screenshots

![Hosts](doc/hosts.png?raw=true "Hosts")

![OVS](doc/ovs.png?raw=true "OVS")

![Init](doc/init.png?raw=true "Init")
