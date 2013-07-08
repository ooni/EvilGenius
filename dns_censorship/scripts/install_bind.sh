apt-get update
apt-get install -y bind9
cp /scripts/named.conf /etc/bind/named.conf
cp /scripts/named.conf.evil /etc/bind/named.conf.evil
cp /scripts/example.com.zone /etc/bind/example.com.zone
echo "nameserver 127.0.0.1" > /etc/resolv.conf
/etc/init.d/bind9 restart
