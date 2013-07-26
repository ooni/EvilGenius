#!/bin/bash
ip l set eth1 up
ip a add $1/24 dev eth1
## delete all existing default routes
while ip route del default; do :; done


## add new default royte
ip route add 0.0.0.0/0 via $2
echo nameserver $3 > /etc/resolv.conf
