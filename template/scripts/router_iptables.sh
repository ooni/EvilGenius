#!/bin/bash

## delete iptables routes
/sbin/iptables -F
/sbin/iptables -X
/sbin/iptables -t nat -F

## enable packet forwarding
/sbin/sysctl -w net.ipv4.ip_forward=1

## set interface forwarding
iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
iptables --append FORWARD --in-interface eth1 -j ACCEPT
iptables --append FORWARD --in-interface eth2 -j ACCEPT
