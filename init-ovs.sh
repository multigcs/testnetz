#!/bin/sh
#
#



ifconfig virbr0 0
cat <<EOF > /etc/dnsmasq.conf
interface=ovsbr
interface=ovsbr2
#dhcp-range=192.168.122.2,192.168.122.254
#dhcp-range=192.168.129.2,192.168.129.254
EOF
killall /usr/sbin/dnsmasq
/etc/init.d/dnsmasq stop
/etc/init.d/dnsmasq start
echo 1 > /proc/sys/net/ipv4/ip_forward

ovs-vsctl add-br ovsbr
ifconfig ovsbr 192.168.122.1

ovs-vsctl add-br ovsbr2
ifconfig ovsbr2 192.168.129.1


ovs-vsctl show
