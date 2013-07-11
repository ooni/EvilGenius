#!/bin/bash

## set interfaces and IP addresses
ip link set eth1 up
ip addr add 10.12.0.1/24 dev eth1
ip link set eth2 up
ip addr add 10.13.0.1/24 dev eth2

## enable packet forwarding
/sbin/sysctl -w net.ipv4.ip_forward=1

## delete iptables routes
/sbin/iptables -F
/sbin/iptables --delete-chain
/sbin/iptables -t nat -F
/sbin/iptables -t nat --delete-chain

## set interface forwarding
iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE

## set interface accept
iptables --append FORWARD --in-interface eth1 -j ACCEPT
iptables --append FORWARD --in-interface eth2 -j ACCEPT
