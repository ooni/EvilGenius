#!/bin/bash

## delete all existing default routes
while ip route del default; do :; done

## add new default royte
ip route add 0.0.0.0/0 via $1
echo nameserver $2 > /etc/resolv.conf
