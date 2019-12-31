# testnetz
easy autoinstaller for os tests using libvirt, docker and openvswitch

* it builds a virtual network using openvswitch

* runs virtaual machines inside kvm using libvirt

* and virtaual containers using docker

* all systems starts with unattended autoinstaller controled by .json files

* you can also install baremetal-systems using PXE



# Quickstart

### install virt-manager, libvirt, tftp-server, dhcp-server, dnsmasq and webserver


### starting web-frontend (only for overview - http://127.0.0.1:8082)

 ./testnetz.py


### check and run ovs init-script:

 sh init-ovs.sh


### start ubuntu installation inside kvm using libvirt and Install-ISO (first start take a while, downloading the Ubuntu-ISO)

 ./init.py -f hosts/ubuntu1910-libvirt.json


### prepare pxe boot: (this take a while, downloading some boot-images and kernels for PXE)

 ./init.py -p


### start centos installation inside kvm using libvirt and PXE-Boot

 ./init.py -f hosts/centos8-pxe.json


### start debian installation inside docker

 ./init.py -f hosts/debian10-docker.json



# Screenshots

![Hosts](doc/hosts.png?raw=true "Hosts")

![OVS](doc/ovs.png?raw=true "OVS")
