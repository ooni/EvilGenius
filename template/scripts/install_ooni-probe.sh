#!/bin/bash
apt-get -y install curl python-setuptools python-dev

echo "Installing Tor..."

echo "deb http://deb.torproject.org/torproject.org precise main" >> /etc/apt/source.list

gpg --keyserver keys.gnupg.net --recv A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89
gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | apt-key add -

apt-get update
apt-get -y install deb.torproject.org-keyring tor tor-geoipdb

apt-get -y install git-core python python-pip python-dev build-essential libdumbnet1 python-dumbnet python-libpcap python-pypcap python-dnspython python-virtualenv virtualenvwrapper tor tor-geoipdb libpcap-dev

echo "Updating to the latest version of PIP"
cd /tmp/

curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python ./get-pip.py ## pip (>=1.3.0) is recommended for security reasons

update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip 0

mkdir /data
cd /data
# TODO replace w/ torproject URL
git clone https://github.com/TheTorProject/ooni-probe.git
cd /data/ooni-probe

echo "Installing dependencies"
pip install pyrex
pip install -r requirements.txt

echo "Installing ooniprobe"
python setup.py install

cd /usr/share/ooni/
make geoip
