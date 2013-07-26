#!/bin/bash
apt-get update
apt-get -y install curl python-setuptools python-dev git libsqlite3-dev curl

echo "Updating to the latest version of PIP"
cd /tmp/

curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
python ./get-pip.py ## pip (>=1.3.0) is recommended for security reasons

update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip 0

#echo "Installing virtualenv and virtualenvwrapper..."

#pip install --upgrade virtualenv virtualenvwrapper
#export WORKON_HOME=~/.virtualenvs && mkdir -p $WORKON_HOME

#source /usr/local/bin/virtualenvwrapper.sh

#mkvirtualenv -a $PWD --unzip-setuptools --setuptools --no-site-packages oonib

echo "Installing Tor..."

echo "deb http://deb.torproject.org/torproject.org precise main" >> /etc/apt/source.list

gpg --keyserver keys.gnupg.net --recv 886DDD89
gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | apt-key add -

apt-get update
apt-get -y install tor-geoipdb tor

mkdir /data
cd /data
git clone https://github.com/TheTorProject/ooni-backend.git
cd /data/ooni-backend

echo "Generating SSL keys"

openssl genrsa -out private.key 4096
openssl req -new -key private.key -out server.csr -subj '/CN=www.example.com/O=Example/C=AU'

openssl x509 -req -days 365 -in server.csr -signkey private.key -out certificate.crt

cp oonib.conf.example oonib.conf

echo "Installing oonib depedencies"
pip install -r requirements.txt --use-mirrors

echo "Installing oonib"
python setup.py install

sudo chmod -R 777 /data/ooni-backend
